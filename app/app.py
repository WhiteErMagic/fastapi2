import fastapi
import pydantic
from lifespan import lifespan
import schema
from dependencies import SessionDependency
import crud
import models
from constants import STATUS_SUCCESS_RESPONSE


app = fastapi.FastAPI(
    title='MyApp',
    version='0.0.1',
    description='...',
    lifespan=lifespan
)


@app.get('/advertisements/{id}', response_model=schema.GetAdvertisementsResponse)
async def get_advertisement(id: int, session: SessionDependency):
    advertisement = await get_advertisement(session, models.Advertisements, id)
    return advertisement.dict


@app.post('/advertisements/', response_model=schema.CreateAdvertisementsResponse)
async def post_advertisement(json: schema.CreateAdvertisementsRequest, session: SessionDependency):
    advertisement = models.Advertisements(**json.model_dump())
    advertisement = await crud.add_item(session, advertisement)
    return advertisement.id


@app.patch('/advertisements/{id}', response_model=schema.UpdateAdvertisementsResponse)
async def patch_advertisement(id: int, json: schema.CreateAdvertisementsRequest, session: SessionDependency):
    advertisement = await crud.get_item(session, models.Advertisements, id)
    await crud.add_item(session, advertisement)
    return advertisement.id


@app.delete('/advertisements/{id}', response_model=schema.DeleteAdvertisementsResponse)
async def delete_advertisement(id: int, session: SessionDependency):
    advertisement = await crud.get_item(session, models.Advertisements, id)
    await delete_advertisement(advertisement)
    return {STATUS_SUCCESS_RESPONSE}