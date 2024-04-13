from bson import ObjectId


class Serializer:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def UserSerializer(user):
    user["id"] = str(user.pop("_id"))
    return Serializer(**user)

