from fastapi.responses import RedirectResponse
from fastapi import Request
from . import router


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(
        key="access_token", 
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response