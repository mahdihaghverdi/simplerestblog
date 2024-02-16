from sqlalchemy import select

from src.repository import BaseRepo
from src.repository.models import TagModel


class TagRepo(BaseRepo):
    model = TagModel

    async def get_or_create(self, tags) -> list[TagModel]:
        tag_model_objects: list[TagModel] = []
        for tag in tags:
            stmt = select(self.model).where(self.model.tag == tag)
            tag_obj = (await self.session.execute(stmt)).scalar_one_or_none()
            if tag_obj is not None:
                tag_model_objects.append(tag_obj)
            else:
                t = self.model(tag=tag)
                tag_model_objects.append(t)
        self.session.add_all(tag_model_objects)
        return tag_model_objects
