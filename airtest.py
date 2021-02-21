import airsim

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# client.moveByMotorPWMsAsync(1,1,1,1,10).join()

client.reset()