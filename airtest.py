import airsim

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

client.moveByVelocityAsync(0,0,-8,5).join()

# client.reset()