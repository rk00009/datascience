from app.planner import create_search_plan


query = input(
    "Enter buyer requirement: "
)


result = create_search_plan(query)


print(
    result.model_dump_json(indent=2)
)