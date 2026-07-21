from fastapi import HTTPException, status


def missing_config_error(keys: list[str]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "MISSING_CONFIG",
            "message": "Required configuration is missing for this feature.",
            "keys": keys,
        },
    )


def feature_unavailable_error(message: str, code: str = "FEATURE_UNAVAILABLE") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"code": code, "message": message, "keys": []},
    )
