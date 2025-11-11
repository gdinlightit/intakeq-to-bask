import csv
import io
import logging
from pydantic import ValidationError
from models import IntakeQPatient
from schemas import Stats


logger = logging.getLogger(__name__)


def format_height_to_feet_inches(inches: str | None) -> str | None:
    """Convert 62 -> 5'2\" """
    try:
        total_inches = int(float(inches))
        feet, remaining_inches = divmod(total_inches, 12)
        return f"{feet}'{remaining_inches}\""
    except (ValueError, TypeError):
        return None


def to_bask_row(patient: IntakeQPatient) -> dict[str, str | None | bool]:
    """Transform IntakeQ patient to Bask Health CSV row."""
    return {
        "First Name": patient.first_name,
        "Last name": patient.last_name,
        "email": patient.email,
        "phone number": patient.mobile_phone
        or patient.home_phone
        or patient.work_phone,
        "DOB": patient.date_of_birth,
        'Height ("5\'9"")': format_height_to_feet_inches(patient.height_in_inches),
        "Weight (lbs)": patient.current_weight,
        "Gender": patient.gender,
        "Sex at birth": patient.sex or patient.gender,
        "Address 1": patient.street_address,
        "Address 2": patient.unit_number,
        "Country": patient.country or "USA",
        "city": patient.city,
        "state": patient.state,
        "zip code": patient.postal_code,
        "Language": "English",
        "SMS consent(did the patient opt into marketing via SMS)": False,
        "Drug": None,
        "current dose": None,
        "last order date": None,
        "allergies": None,
        "current medications": patient.current_medications,
    }


def transform_csv(input_csv: bytes) -> tuple[bytes, Stats]:
    """Transform IntakeQ CSV to Bask Health format."""
    reader = csv.DictReader(f=io.StringIO(input_csv.decode("utf-8")), delimiter=";")

    valid_rows, failed = [], 0

    for row_num, row in enumerate(iterable=reader, start=2):
        try:
            valid_rows.append(to_bask_row(IntakeQPatient(**row)))
        except ValidationError as e:
            failed += 1
            logger.error(
                f"Row {row_num} failed: {row.get('ClientId', 'unknown')} - {e}"
            )

    output = io.StringIO()

    writer = csv.DictWriter(output, fieldnames=list(valid_rows[0].keys()))
    writer.writeheader()
    writer.writerows(valid_rows)

    stats = Stats(
        total=len(valid_rows) + failed,
        successful=len(valid_rows),
        failed=failed,
    )

    logger.info(f"Transformed {stats.successful}/{stats.total} patients")

    return output.getvalue().encode("utf-8"), stats
