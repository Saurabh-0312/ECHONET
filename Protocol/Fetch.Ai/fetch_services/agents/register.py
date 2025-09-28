import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Decibal_Echonet_agent",
    "https://echonet-decibal-agent.onrender.com",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key="eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjA5ODc2NzcsImlhdCI6MTc1ODM5NTY3NywiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI4ZTM0YzM2OGI3YmQ2MDY1ZWM3ZjkwMTgiLCJzY29wZSI6ImF2Iiwic3ViIjoiYjIxNjVjZTJjYmM4ODQ4ZDU0MjY4NjA1Yzc2Y2YzZTUzYmY3MmZkM2YzNzAxZmJjIn0.kYYZgca83_v7WqYmfFEGn6Ki7iEmRyWwfZSsg4Vak4ESDUOCWkajNBuBbZAXoy5VfohJVCR18O2AUe_3kRa0PywGpL_E-hqMJUvod5K_lVW0NDqpVRERHknGT8e8d-vLgYkRtnP-IFSkI2Npn2Rmv7H-WMmmty8U7JAy0P-Zvq9TSq8UrpDD3Hg5gikipnRL4RxarTgQNY-3ZbYTXweTPE6-QTYzjE9IB8rLFdmun_P6y1_IkjG0pleaYpZz-8Z1wohlAX52vTB8nl-gWVOWXv7tvF47qk2Q08-W96zWLKGsIXF4YZ2Ol0BcErY--OQ7VhxJQZF5tpgf1NTlJSiy-w",
        agent_seed_phrase="decibal_agent_super_secret_seed_phrase",
    ),
)