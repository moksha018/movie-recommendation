document.addEventListener("DOMContentLoaded", function () {
    const sliderItems = document.querySelectorAll(".slider-item");
    const sliderControlButtons = document.querySelectorAll(".slider-control-button");

    let currentIndex = 0;
    let interval = 5000; // Interval in milliseconds (5 seconds)
    let carouselInterval;

    const switchToCard = function (index) {
        sliderItems.forEach(item => item.classList.remove("active"));
        sliderControlButtons.forEach(item => item.classList.remove("active"));

        currentIndex = index;
        sliderItems[currentIndex].classList.add("active");
        sliderControlButtons[currentIndex].classList.add("active");
    };

    const switchToNextCard = function () {
        currentIndex = (currentIndex + 1) % sliderItems.length;
        switchToCard(currentIndex);
    };

    const startCarousel = function () {
        carouselInterval = setInterval(switchToNextCard, interval);
    };

    const resetCarousel = function () {
        clearInterval(carouselInterval);
        startCarousel();
    };

    startCarousel();

    sliderControlButtons.forEach((control, index) => {
        control.addEventListener("click", function () {
            resetCarousel();
            switchToCard(index);
        });
    });

    sliderItems.forEach((item, index) => {
        item.addEventListener("click", function () {
            resetCarousel();
            switchToCard(index);
        });
    });

    // Activate the first movie card initially
    switchToCard(0);
});
