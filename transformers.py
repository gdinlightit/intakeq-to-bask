from dataclasses import dataclass
import logging
import csv
from io import StringIO

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TransformStats:
    total: int
    successful: int
    failed: int


def format_name(name: str | None) -> str:
    if not name:
        return ""
    return name.strip().lower().title()


def format_height_to_feet_inches(inches: str | None) -> str:
    """Convert inches to 5'9" format."""
    if not inches:
        return ""
    try:
        total_inches = int(float(inches))
        feet, remaining_inches = divmod(total_inches, 12)
        return f"{feet}'{remaining_inches}\""
    except (ValueError, TypeError):
        logger.warning(f"Invalid height value: {inches}")
        return ""


def transform_intakeq_to_bask(row: dict) -> dict:
    """Transform single IntakeQ row to Bask Health format."""
    return {
        "First Name": format_name(row.get("FirstName")),
        "Last name": format_name(row.get("LastName")),
        "email": row.get("Email", ""),
        "phone number": row.get("MobilePhone", ""),
        "DOB": row.get("DateOfBirth", ""),
        'Height ("5\'9")': format_height_to_feet_inches(row.get("Height In Inches")),
        "Weight (lbs)": row.get("Current Weight", ""),
        "Gender": row.get("Gender", ""),
        "Sex at birth": row.get("Sex", ""),
        "Address 1": row.get("StreetAddress", ""),
        "Address 2": row.get("UnitNumber", ""),
        "Country": row.get("Country", ""),
        "city": row.get("City", ""),
        "state": row.get("State", ""),
        "zip code": row.get("PostalCode", ""),
        "Language": row.get("Language", "English"),  # TODO: validate with Bask/Arsenio
        "SMS consent(did the patient opt into marketing via SMS)": True,  # TODO: validate with Bask/Arsenio
        "Drug": "",
        "current dose": "",
        "last order date": "",
        "allergies": "",
        "current medications": row.get("Current Medications", ""),
    }


def transform_csv(input_csv: bytes) -> tuple[bytes, TransformStats]:
    """Transform entire CSV from IntakeQ format to Bask Health format."""
    logger.info("Starting CSV transformation")

    output = StringIO()

    reader = csv.DictReader(f=StringIO(input_csv.decode("utf-8")), delimiter=";")
    writer = csv.DictWriter(output, fieldnames=transform_intakeq_to_bask({}).keys())

    row_count, error_count = 0, 0

    writer.writeheader()
    for row in reader:
        try:
            writer.writerow(transform_intakeq_to_bask(row))
            row_count += 1
        except Exception as e:
            error_count += 1
            logger.error(
                f"Error transforming row | Client ID: {row.get('ClientId')} | Message: {str(e)}"
            )

    stats = TransformStats(
        total=row_count + error_count, successful=row_count, failed=error_count
    )

    logger.info(
        f"CSV transformation complete | "
        f"Total: {stats.total} | "
        f"Successful: {stats.successful} | "
        f"Failed: {stats.failed}"
    )

    return output.getvalue().encode("utf-8"), stats
