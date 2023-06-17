import numpy as np
import pandas as pd
import do_mpc
from casadi import *

from Environment import Environment
from MPCAdaptor import MPCAdaptor

      
model_type = 'discrete' # either 'discrete' or 'continuous'
model = do_mpc.model.Model(model_type)
order = 4 # number of x
numCP = 6 # number of control parameters

# x, which is performance indicators
x_1_cost = model.set_variable(var_type='_x', var_name='x_1_cost', shape=(1,1))
x_2_temp = model.set_variable(var_type='_x', var_name='x_2_temp', shape=(1,1))
x_3_moist = model.set_variable(var_type='_x', var_name='x_3_moist', shape=(1,1))
x_4_light = model.set_variable(var_type='_x', var_name='x_4_light', shape=(1,1))

# u, which is control parameters
u_1_ac = model.set_variable(var_type='_u', var_name='u_1_ac')
u_2_fan = model.set_variable(var_type='_u', var_name='u_2_fan')
u_3_humi = model.set_variable(var_type='_u', var_name='u_3_humi')
u_4_curt = model.set_variable(var_type='_u', var_name='u_4_curt')
u_5_light = model.set_variable(var_type='_u', var_name='u_5_light')
u_6_al = model.set_variable(var_type='_u', var_name='u_6_al')

# time varying parameter, which is context/environment
c_1_light = model.set_variable('_tvp', 'c_1_light') 
c_2_temp = model.set_variable('_tvp', 'c_2_temp')
c_3_moist = model.set_variable('_tvp', 'c_3_moist')

x_1_next = 20 * u_1_ac + 5 * u_2_fan + 5 * u_3_humi + 5 * u_5_light + 5 * u_6_al
x_2_next = x_2_temp + 0.6 * u_1_ac * (26 - x_2_temp) - 0.2 * u_2_fan + 0.3 * (c_2_temp - x_2_temp)
x_3_next = x_3_moist + 0.1 * u_3_humi * (1 - x_3_moist) + 0.03 * (c_3_moist - x_3_moist)
x_4_next = u_5_light * (100 - c_1_light) + c_1_light

model.set_rhs('x_1_cost', x_1_next)
model.set_rhs('x_2_temp', x_2_next)
model.set_rhs('x_3_moist', x_3_next)
model.set_rhs('x_4_light', x_4_next)

model.setup()


# define mpc setting

mpc = do_mpc.controller.MPC(model)
setup_mpc = {
    'n_horizon': 3,
    't_step': 1,
    'n_robust': 1,
    'store_full_solution': True,
}
mpc.set_param(**setup_mpc)

# define objective function
mterm = 0*x_1_cost

weights = [0.1, 0.4, 0.2, 0.3]
lterm = weights[0] * (x_1_cost / 130)**2 + weights[1] * ((x_2_temp - 25) / 10)**2 + weights[2] * (x_3_moist - 0.6)**2 + weights[3] * (1 - x_4_light / 100)**2

mpc.set_objective(mterm=mterm, lterm=lterm)

mpc.set_rterm(
    u_1_ac=1e-2,
    u_2_fan=1e-2,
    u_3_humi=1e-2
)

# define bounds
mpc.bounds['lower','_u', 'u_1_ac'] = 0
mpc.bounds['lower','_u', 'u_2_fan'] = 0
mpc.bounds['lower','_u', 'u_3_humi'] = 0
mpc.bounds['lower','_u', 'u_4_curt'] = 0
mpc.bounds['lower','_u', 'u_5_light'] = 0
mpc.bounds['lower','_u', 'u_6_al'] = 0

mpc.bounds['upper','_u', 'u_1_ac'] = 3
mpc.bounds['upper','_u', 'u_2_fan'] = 3
mpc.bounds['upper','_u', 'u_3_humi'] = 3
mpc.bounds['upper','_u', 'u_4_curt'] = 1
mpc.bounds['upper','_u', 'u_5_light'] = 1
mpc.bounds['upper','_u', 'u_6_al'] = 1


# environment 
Env = Environment()
Env.generate()

tvp_prediction = mpc.get_tvp_template()
def tvp_fun(t_now):
    pvalue_list = []
    pvalue_list.append([Env.lightList[int(t_now)],Env.tempList[int(t_now)],Env.moistList[int(t_now)]])
    for t in range(3):
        #pvalue = predict(req_model, res_model, int(t_now + t + 1))
        #pvalue_list.append(pvalue)
        pvalue_list.append([Env.lightList[int(t_now + t + 1)],Env.tempList[int(t_now + t + 1)],Env.moistList[int(t_now + t + 1)]])
    tvp_prediction['_tvp'] = pvalue_list
    return tvp_prediction

mpc.set_tvp_fun(tvp_fun)

# mpc setup end
mpc.setup()

# simulator
simulator = do_mpc.simulator.Simulator(model)
simulator.set_param(t_step = 1)
tvp_sim = simulator.get_tvp_template()

def tvp_fun_sim(t_now):
    tvp_sim['c_1_light'] = Env.lightList[int(t_now)]
    tvp_sim['c_2_temp'] = Env.tempList[int(t_now)]
    tvp_sim['c_3_moist'] = Env.moistList[int(t_now)]
    return tvp_sim

simulator.set_tvp_fun(tvp_fun_sim)
simulator.setup()

x0 = np.array([0, Env.tempList[0], Env.moistList[0], 0]).reshape(-1,1)
mpc.x0 = x0
mpc.set_initial_guess()

u0 = np.array([0,0,0,0,0,0]).reshape(-1,1)

mpcAdaptor = MPCAdaptor(Env)

cpList = []
piList = []

timeLimit = 48
t = 0

for i in range(timeLimit):
    # update environment

    # whether adapt mpc setting or not
    mpcAdaptor.adapt(t, mpc)
    
    # mpc control 
    x_p = simulator.make_step(u0)
    piList.append(x_p)
    u0 = mpc.make_step(x_p)
    cpList.append(u0)
    # effect control to system
    
    t = t + 1

for i in range(timeLimit):
    print("=============================")
    print("time: " + str(i))
    print("Environment variable values:")
    print("temperature:" + str(Env.tempList[i]))
    print("moisture:" + str(Env.moistList[i]))
    print("lightning:" + str(Env.lightList[i]))
    print("\n")
    
    print("Performace Indicators:")
    print("cost: " + str(piList[i][0]))
    print("temp: " + str(piList[i][1]))
    print("moist: " + str(float(piList[i][2])))
    print("light: " + str(piList[i][3]))
    print("\n")

    print("Control Parameters:")
    print("ac: "+ str(round(float(cpList[i][0]))))
    print("fan: "+ str(round(float(cpList[i][1]))))
    print("humi: "+ str(round(float(cpList[i][2]))))
    print("curt: "+ str(round(float(cpList[i][3]))))
    print("light: "+ str(round(float(cpList[i][4]))))
    print("al: "+ str(round(float(cpList[i][5]))))
    print("\n")