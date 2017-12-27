#!/bin/bash

# initwelcome.sh: sets welcome screen
# Execute once only

# Greeting Text
curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type":"greeting",
  "greeting":{
    "text":"Hi {{user_first_name}}, welcome to this bot."
  }
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$EAAdIkAG76KIBAPR8JCfVT0GyZBQQ41lYhBGLQtA9bqYBuC6wldmfZBLyCUWadZC15TaHuulZAtf7iZCcuc34y9aTrSZAn7PpvClKxKmvkGFrMqVDrkYjdSQBd4Ngj84LSlULaT8nM2FJBoYH8N4hlJ1sxgGzG2UJLapvMtNzKdZCgZDZD"

# Get Started button
curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type":"call_to_actions",
  "thread_state":"new_thread",
  "call_to_actions":[
    {
      "payload":"Get Started"
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$EAAdIkAG76KIBAPR8JCfVT0GyZBQQ41lYhBGLQtA9bqYBuC6wldmfZBLyCUWadZC15TaHuulZAtf7iZCcuc34y9aTrSZAn7PpvClKxKmvkGFrMqVDrkYjdSQBd4Ngj84LSlULaT8nM2FJBoYH8N4hlJ1sxgGzG2UJLapvMtNzKdZCgZDZD"