import strawberry

from strawberry.tools import create_type
from strawberry.fastapi import GraphQLRouter

from fastapi import FastAPI

from os import getenv

# override Context scalar
from otypes import Context

# import all queries and mutations
from queries import queries

# check whether running in debug mode
DEBUG = getenv("SERVICES_DEBUG", "False").lower() in ("true", "1", "t")

# create query types
Query = create_type("Query", queries)

# override context getter
async def get_context() -> Context:
    return Context()


# initialize federated schema
schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,
)

# serve API with FastAPI router
gql_app = GraphQLRouter(
    schema, 
    graphiql=True,
    context_getter=get_context
)
app = FastAPI(debug=DEBUG)

app.include_router(gql_app, prefix="/graphql")
