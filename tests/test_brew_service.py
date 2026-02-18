# tests/test_brew_service.py
import pytest

from app.services.brew_service import calculate_water, tips_for_brew


class TestCalculateWater:
    def test_basic(self):
        assert calculate_water(18, 16) == 288.0

    def test_rounding(self):
        # 18.5 * 15.5 = 286.75 → arrotondato a 1 decimale
        assert calculate_water(18.5, 15.5) == 286.8

    def test_small_dose(self):
        assert calculate_water(7, 12) == 84.0


class TestTipsForBrew:
    def test_no_rating(self):
        tips = tips_for_brew(None)
        assert len(tips) == 1
        assert "rating" in tips[0]

    def test_low_rating_boundary(self):
        # rating <= 5 → 2 suggerimenti
        assert len(tips_for_brew(1)) == 2
        assert len(tips_for_brew(5)) == 2

    def test_medium_rating_boundary(self):
        # 6 <= rating <= 7 → 1 suggerimento
        assert len(tips_for_brew(6)) == 1
        assert len(tips_for_brew(7)) == 1

    def test_high_rating_boundary(self):
        # rating >= 8 → 1 suggerimento positivo
        tips = tips_for_brew(8)
        assert len(tips) == 1
        assert "Ottimo" in tips[0]
        assert len(tips_for_brew(10)) == 1

    def test_low_rating_content(self):
        tips = tips_for_brew(3)
        assert any("macinatura" in t for t in tips)
        assert any("temperatura" in t.lower() or "ratio" in t.lower() for t in tips)
