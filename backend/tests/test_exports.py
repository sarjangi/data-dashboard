"""Tests for export endpoint helpers."""

import pytest
from fastapi import HTTPException

from app.api.exports import export_pdf


@pytest.mark.asyncio
async def test_export_pdf_returns_not_implemented():
    """PDF export should fail explicitly until implemented."""
    with pytest.raises(HTTPException) as error:
        await export_pdf()

    assert error.value.status_code == 501
    assert error.value.detail == "PDF export is not implemented yet"
