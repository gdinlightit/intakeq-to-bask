from pydantic import BaseModel, field_validator, Field


class IntakeQPatient(BaseModel):
    client_id: str = Field(alias="ClientId")

    first_name: str | None = Field(alias="FirstName")
    last_name: str | None = Field(alias="LastName")

    email: str | None = Field(default=None, alias="Email")
    mobile_phone: str | None = Field(default=None, alias="MobilePhone")
    home_phone: str | None = Field(default=None, alias="HomePhone")
    work_phone: str | None = Field(default=None, alias="WorkPhone")

    date_of_birth: str | None = Field(default=None, alias="DateOfBirth")
    gender: str | None = Field(default=None, alias="Gender")
    sex: str | None = Field(default=None, alias="Sex")

    street_address: str | None = Field(default=None, alias="StreetAddress")
    unit_number: str | None = Field(default=None, alias="UnitNumber")
    city: str | None = Field(default=None, alias="City")
    state: str | None = Field(default=None, alias="State")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    country: str | None = Field(default=None, alias="Country")

    current_weight: str | None = Field(default=None, alias="Current Weight")
    height_in_inches: str | None = Field(default=None, alias="Height In Inches")
    current_medications: str | None = Field(default=None, alias="Current Medications")

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if not v:
            return None
        return v

    @field_validator("mobile_phone", "home_phone", "work_phone")
    @classmethod
    def clean_phone(cls, v: str | None) -> str | None:
        if not v:
            return None
        cleaned = "".join(c for c in v if c.isdigit())
        return cleaned or None

    @field_validator("current_medications")
    @classmethod
    def normalize_medications(cls, v: str | None) -> str | None:
        if not v:
            return None
        return v

    @field_validator("height_in_inches", "current_weight")
    @classmethod
    def validate_numeric(cls, v: str | None) -> str | None:
        if not v:
            return None
        try:
            float(v)
            return v
        except ValueError:
            return None
