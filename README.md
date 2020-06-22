# API Gateway Approached Microservices, Authentication with FastAPI
- This repo is composed of a bunch of small microservices considering api gateway approach
- Expected number of microservices was two, but considering that services
  should not create dependency on each other to prevent SPOF, also to prevent duplicate codes,
  i decided to put one api gateway in front that does JWT authentication for both services
  which i am insired by Netflix/Zuul
- We have 3 services including gateway.
- Only gateway can access internal microservices through the internal network (users, orders)

## Services
- gateway: Built on top of FastAPI, simple api gateway which its only duty is to make proper
  routing while also handling authentication and authorization
- users (a.k.a admin): Keeps user info in its own fake db (file system).
  Can be executed simple CRUD operations through the service. There is also another
  endpoint for login, but client is abstracted from real response. Thus, gateway service
  will handle login response and generate jwt token accordingly.
- orders: Users (subscribed ones - authentication) can create and view (their - authorization) orders.

## Running
- check ./gateway/.env => 2 services url are defined based on twelvefactor conf
- docker-compose up --build
- visit => http://localhost:8001/docs

# Example requests
- There are already created 2 users in users db
- get api token with admin user
`
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"username":"admin","password":"a"}' \
     http://localhost:8001/api/login
`
- You'll see something similar to below
`
{"access_token":"***","token_type":"bearer"}
`
- use this token to make administrative level requests
`
curl --header "Content-Type: application/json" \
     --header "Authorization: Bearer ***" \
     --request GET \
     http://localhost:8001/api/users
`
- Similar trials can be also done with default user to create & view orders

## IMPORTANT NOTES & POSSIBLE TODOs
- Tried to use coroutines on especially i/o operations to boost the performance of gateway. (aiohttp)
- Again, non-blocking db client library is used. (tortoise-orm)
- Tried to use dependency injection on gateway api new router, because i am thinking  to
  feed this project and make it open source for other people as well.
- Tried to implement declarative way for api gateway rules, for now it works
  based on decorator, but my purpose is to make it more declarative like using
  yaml configuration
- Since it is executed with docker-compose file, it shouldn't be considered as production ready (a.k.a scalability)
- API gateway approach is considered, also inspired by Zuul, event-driven approach can be easily applied in case needed.
- Authentication and authorization are seperated from the services to keep things clean, one service does for all.
- JWT token are generated in gateway service and other services behind the gateway receive a seperated
  header called request-user-id to use user info in jwt token.
- Unit tests are written for only users service to show up my understanding of.
  > under ./users/tests/*
  > example run: docker exec -ti <docker users container id> python -m tests.auth
- Docstrings are written for only gateway service for a couple of methods to show up my understanding of.
  > ./gateway/network.py[make_request], ./gateway/core.py[route]
- thread-safety was not considered especially on fake users service since we
  use file operations, and it might produce race conditions
- Another autorization level can be added into private-network services
  checking if request-user-id header exists
- hashed_password might be shadowed in users response
- API versioning might be considered
- JWT token TTL can be changed under ./gateway/conf.py[settings]

## Overall Diagram
![ScreenShot](https://raw.github.com/baranbartu/microservices-with-fastapi/master/diagram.png)
