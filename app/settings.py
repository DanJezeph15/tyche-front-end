from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mapbox_token: str = ''
    password: str = ''
    model_config = SettingsConfigDict(env_file='_localsettings.py', extra='allow')


app_settings = Settings()
