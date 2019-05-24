#
#                             _ooOoo_
#                            o8888888o
#                            88" . "88
#                            (| -_- |)
#                            O\  =  /O
#                         ____/`---'\____
#                       .'  \\|     |//  `.
#                      /  \\|||  :  |||//  \
#                     /  _||||| -:- |||||-  \
#                     |   | \\\  -  /// |   |
#                     | \_|  ''\---/''  |   |
#                     \  .-\__  `-`  ___/-. /
#                   ___`. .'  /--.--\  `. . __
#                ."" '<  `.___\_<|>_/___.'  >'"".
#               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#               \  \ `-.   \_ __\ /__ _/   .-` /  /
#          ======`-.____`-.___\_____/___.-`____.-'======
#                             `=---='
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                     佛祖保佑        永无BUG
#

import MalmoPython
import os
import sys
import time
import json
from agent import Agent
import random





if __name__ == "__main__":

    # read mission
    with open('mission.xml','r') as iFile:
        missionXML = iFile.read()
        iFile.close()

    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR:', e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)
    
    iRepeat = 1000
    agent = Agent()

    for i in range(iRepeat):
        agent.pastActions = []
        my_mission = MalmoPython.MissionSpec(missionXML, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        # Start mission
        max_retries = 3
        my_client_pool = MalmoPython.ClientPool()
        my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Monster Killer")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)
        
        # Wait until mission starts:
        print("Waiting for the mission to start")
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
        print()
        print("Mission started: ",i, " with n = 10"," and with eps = ",agent.epsilon)


        # Mission processing, TODO: move actions to agent class
        observations = agent.getObservations(world_state)
        time.sleep(1)


        agent.run(agent_host)
        

        print("Mission ended")
        if (-100000,1) in agent.q_table:
            del agent.q_table[(-100000,1)]
        for state in agent.q_table:
            lowest = -10000
            theaction = 0
            for action in agent.q_table[state]:
                if agent.q_table[state][action] > lowest:
                    lowest = agent.q_table[state][action]
                    theaction = action
            print("On state: ",state," best action is ",theaction," with q_value of ", lowest)
        agent.pastActions = []
        agent.MonsterHeart = 20
        agent.Heart = 20
        agent.action = 0
        agent.weapon = 1
        tp_command = "tp 0 255 0"
        agent_host.sendCommand(tp_command)
        time.sleep(1) # sleep for 1s, otherwise it will not restart

        agent.epsilon-=0.01




