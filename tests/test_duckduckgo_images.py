import allure
import pytest

# @pytest.mark.parametrize("book_name", ["The miserable", "Blindness"])
@pytest.mark.parametrize("book_name", ["Miserable"])
def test_third_image_is_public_domain_and_large_enough(searched_page, book_name):
    with allure.step("Open Images and apply filters"):
        searched_page.open_images()
        searched_page.apply_filters()

    with allure.step("Validate 3rd image source and size"):
        results = searched_page.get_results()
        assert len(results) >= 3, f"Expected >= 3 results, got {len(results)}"

        third = results[2]
        source = searched_page.source_of(third)
        width, height = searched_page.size_of(third)

        # assert "kobo.com" in source.lower(), f"Unexpected source: {source}"
        assert "publicdomainpictures.net" in source.lower(), f"Unexpected source: {source}"
        assert width > 1000 and height > 1000, f"Image too small: {width}x{height}"
