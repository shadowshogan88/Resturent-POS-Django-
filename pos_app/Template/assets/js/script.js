/*
Author       : Dreamguys
Template Name: POS - Bootstrap Admin Template
*/


$(document).ready(function(){

	// Variables declarations
	const $wrapper = $('.main-wrapper');
	const $overlay = $('<div class="sidebar-overlay"></div>');
	$overlay.insertBefore('.main-wrapper');


	// Toggle Mobile Menu
	$(document).on('click', '#mobile_btn', function (e) {
		e.preventDefault();
		$wrapper.toggleClass('slide-nav');
		$overlay.toggleClass('opened');
		$('html').toggleClass('menu-opened');
	});

	// Close sidebar on close button click
	$(document).on('click', '.sidebar-close, .sidebar-overlay', function () {
		$wrapper.removeClass('slide-nav');
		$overlay.removeClass('opened');
		$('html').removeClass('menu-opened');
	});

	// Table Responsive
	setTimeout(function () {
		$(document).ready(function () {
			$('.table').parent().addClass('table-responsive');
		});
	}, 1000);

	// Datatable
	if($('.datatable').length > 0) {
		$('.datatable').DataTable({
			"bFilter": true,
			"sDom": 'fBtlp',  
			"ordering": false,
			"language": {
				search: ' ',
				sLengthMenu: '_MENU_',
				searchPlaceholder: "Search",
				sLengthMenu: ' _MENU_ Entries',
				info: "_START_ - _END_ of _TOTAL_ items",
				paginate: {
					next: ' Next <i class="icon-chevron-right"></i>',
					previous: '<i class="icon-chevron-left"></i> Prev'
				},
			 },
			initComplete: (settings, json)=>{
				$('.dt-search').appendTo('#tableSearch');
				$('.dt-search').appendTo('.search-input');

			},	
		});
	}


	// Datetimepicker
	if($('.datetimepicker').length > 0 ){
		$('.datetimepicker').datetimepicker({
			format: 'DD-MM-YYYY',
			icons: {
				up: "fas fa-angle-up",
				down: "fas fa-angle-down",
				next: 'fas fa-angle-right',
				previous: 'fas fa-angle-left'
			}
		});
	}

	// Date Range Picker
	if ($('.daterangepick').length > 0) {
		const start = moment().subtract(29, "days");
		const end = moment();
		const report_range = (start, end) => {
			$(".daterangepick span").html(`${start.format("D MMM YY")} - ${end.format("D MMM YY")}`);
		};
		$(".daterangepick").daterangepicker(
			{
				startDate: start,
				endDate: end,
				ranges: {
					'Today': [moment(), moment()],
					'Yesterday': [moment().subtract(1, "days"), moment().subtract(1, "days")],
					"Last 7 Days": [moment().subtract(6, "days"), moment()],
					"Last 30 Days": [moment().subtract(29, "days"), moment()],
					"This Month": [moment().startOf("month"), moment().endOf("month")],
					"Last Month": [
						moment().subtract(1, "month").startOf("month"),
						moment().subtract(1, "month").endOf("month")
					]
				}
			},
			report_range
		);
		report_range(start, end);
	}

		// Select 2 Search
	if ($('.select2').length > 0) {
		$('.select2').select2({
			// Set to 0 to always show search, or a number like 10 
			// to show only when there are 10+ results
			minimumResultsForSearch: 0, 
			width: '100%'
		});
	}

	// Select 2
	if ($('.select').length > 0) {
		$('.select').select2({
			minimumResultsForSearch: -1,
			width: '100%'
		});
	}

	// Select Table Checkbox
	$('#select-all').on('change', function () {
		$('.form-check.form-check-md input[type="checkbox"]').prop('checked', this.checked);
	});

	// Counter 
	if($('.counter').length > 0) {
		$('.counter').counterUp({
			delay: 20,
			time: 2000
		});
	}

	// Toggle Password
	if ($('.toggle-password').length > 0) {
		$(document).on('click', '.toggle-password', function () {
			const $icon = $(this).find('i');
			const $input = $(this).closest('.input-group').find('.pass-input');
			if ($input.attr('type') === 'password') {
				$input.attr('type', 'text');
				$icon.removeClass('icon-eye-off').addClass('icon-eye');
			} else {
				$input.attr('type', 'password');
				$icon.removeClass('icon-eye').addClass('icon-eye-off');
			}
		});
	}

	// Sidebar
	var Sidemenu = function() {
		this.$menuItem = $('.sidebar-menu a');
	};

	function init() {
		var $this = Sidemenu;
		$('.sidebar-menu a').on('click', function(e) {
			if($(this).parent().hasClass('submenu')) {
				e.preventDefault();
			}
			if(!$(this).hasClass('subdrop')) {
				$('ul', $(this).parents('ul:first')).slideUp(250);
				$('a', $(this).parents('ul:first')).removeClass('subdrop');
				$(this).next('ul').slideDown(350);
				$(this).addClass('subdrop');
			} else if($(this).hasClass('subdrop')) {
				$(this).removeClass('subdrop');
				$(this).next('ul').slideUp(350);
			}
		});
		$('.sidebar-menu ul li.submenu a.active').parents('li:last').children('a:first').addClass('active').trigger('click');
	}

	// Sidebar
	var Colsidemenu = function() {
		this.$menuItems = $('.sidebar-right a');
	};

	function colinit() {
    var $this = Colsidemenu;

    // Unbind previous click handlers to avoid duplicates
		$('.sidebar-right ul a').off('click').on('click', function (e) {

			// Check if parent has 'submenu' class
			if ($(this).parent().hasClass('submenu')) {
				e.preventDefault();
				console.log("1");
			}

			// If this is not currently expanded
			if (!$(this).hasClass('subdrop')) {
				// Close all sibling submenus
				$(this).closest('ul').find('ul').slideUp(250);
				$(this).closest('ul').find('a').removeClass('subdrop');

				// Open the clicked submenu
				$(this).next('ul').slideDown(350);
				$(this).addClass('subdrop');
				console.log("0");

			} else { // If already expanded, collapse it
				$(this).removeClass('subdrop');
				$(this).next('ul').slideUp(350);
				console.log("3");
			}
		});

		// Open submenu if an active item is inside
		$('.sidebar-right ul li.submenu a.active').parents('li').children('a').addClass('active subdrop');
		$('.sidebar-right ul li.submenu a.active').parents('ul').slideDown(350);
	}

	colinit();


	
	// Sidebar Initiate
	init();
	$(document).on('mouseover', function(e) {
        e.stopPropagation();
        if ($('body').hasClass('mini-sidebar')) {
            var targ = $(e.target).closest('.sidebar, .header-left').length;
            if (targ) {
                $('body').addClass('expand-menu');
                $('.subdrop + ul').slideDown();
            } else {
                $('body').removeClass('expand-menu');
                $('.subdrop + ul').slideUp();
            }
            return false;
        }
		if ($('body').hasClass('mini-sidebar')) {
            var targ = $(e.target).closest('.sidebar, .header-left').length;
            if (targ) {
                $('body.layout-box-mode').addClass('expand-menu');
                $('.subdrop + ul').slideDown();
            } else {
                $('body').removeClass('expand-menu');
                $('.subdrop + ul').slideUp();
            }
            return false;
        }
    });

	// Toggle Button
	$(document).on('click', '#toggle_btn', function () {
		const $body = $('body');
		const $html = $('html');
		const isMini = $body.hasClass('mini-sidebar');
	
		if (isMini) {
			$body.removeClass('mini-sidebar');
			$(this).addClass('active');
			localStorage.setItem('screenModeNightTokenState', 'night');
			setTimeout(function () {
				$(".header-left").addClass("active");
			}, 100);
		} else {
			$body.addClass('mini-sidebar');
			$(this).removeClass('active');
			localStorage.removeItem('screenModeNightTokenState');
			setTimeout(function () {
				$(".header-left").removeClass("active");
			}, 100);
		}

	
		return false;
	});
		
	// Tooltip
	if($('[data-bs-toggle="tooltip"]').length > 0) {
		var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
		var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
			return new bootstrap.Tooltip(tooltipTriggerEl)
		})
	}

		// Initialize Flatpickr on elements with data-provider="flatpickr"
		document.querySelectorAll('[data-provider="flatpickr"]').forEach(el => {
			const config = {
				disableMobile: true
			};
			if (el.hasAttribute('data-date-format')) {
				config.dateFormat = el.getAttribute('data-date-format');
			}
			if (el.hasAttribute('data-enable-time')) {
				config.enableTime = true;
				config.dateFormat = config.dateFormat ? `${config.dateFormat} H:i` : 'Y-m-d H:i';
			}
			if (el.hasAttribute('data-altFormat')) {
				config.altInput = true;
				config.altFormat = el.getAttribute('data-altFormat');
			}
			if (el.hasAttribute('data-minDate')) {
				config.minDate = el.getAttribute('data-minDate');
			}
			if (el.hasAttribute('data-maxDate')) {
				config.maxDate = el.getAttribute('data-maxDate');
			}
			if (el.hasAttribute('data-default-date')) {
				const defaultDate = el.getAttribute('data-default-date');
				// Check if it's a valid date string
				if (!["true", "false", "", null].includes(defaultDate) && !isNaN(Date.parse(defaultDate))) {
					config.defaultDate = defaultDate;
				}
			}
			if (el.hasAttribute('data-multiple-date')) {
				config.mode = 'multiple';
			}
			if (el.hasAttribute('data-range-date')) {
				config.mode = 'range';
			}
			if (el.hasAttribute('data-inline-date')) {
				config.inline = true;
				const inlineDate = el.getAttribute('data-inline-date');
				if (!["true", "false", "", null].includes(inlineDate) && !isNaN(Date.parse(inlineDate))) {
					config.defaultDate = inlineDate;
				}
			}
			if (el.hasAttribute('data-disable-date')) {
				config.disable = el.getAttribute('data-disable-date').split(',');
			}
			if (el.hasAttribute('data-week-number')) {
				config.weekNumbers = true;
			}
			flatpickr(el, config);
		});
		
		// Add input in modal

		// Add new row (works for all groups)
			$(document).on("click", ".addRowBtn", function () {
				let target = $(this).data("target");  // get group id
				let template = $("#" + target + "-template").clone();

				template.removeClass("d-none rowTemplate");
				$("#" + target).append(template);
			});

			// Delete row (works for all groups)
			$(document).on("click", ".deleteRowBtn", function () {
				$(this).closest(".row").remove();
			});

		//Copy to Clipboard
		$(document).on("click", ".copytoclipboard", function () {
			let text = document.getElementById("copytext").innerText;
			navigator.clipboard.writeText(text)
				.then(() => alert("Copied to clipboard!"))
				.catch(err => console.error("Failed to copy: ", err));
			});
	
	// Timer
	$(".card").each(function () {
		const card = $(this);
		const btn = card.find(".timer-btn");
		const icon = btn.find("i");
		const label = btn.find(".label");
		const timeText = btn.find(".time");

		// Timer state per card
		let seconds = 0;
		let timerInterval = null;

		function formatTime(sec) {
			const m = String(Math.floor(sec / 60)).padStart(2, "0");
			const s = String(sec % 60).padStart(2, "0");
			return `${m}:${s}`;
		}

		function startTimer() {
			if (timerInterval) return;
			btn.addClass("running");
			icon.removeClass("icon-play").addClass("icon-pause");
			label.text("Pause");

			timerInterval = setInterval(() => {
				seconds++;
				timeText.text(formatTime(seconds));
			}, 1000);
		}

		function pauseTimer() {
			if (!timerInterval) return;
			clearInterval(timerInterval);
			timerInterval = null;
			btn.removeClass("running");
			icon.removeClass("icon-pause").addClass("icon-play");
			label.text("Play");
		}

		btn.on("click", function (e) {
			e.preventDefault(); // prevent default link behavior

			if (btn.hasClass("running")) {
				pauseTimer();
			} else {
				startTimer();
			}
		});
	});



		// Attach keydown event only when modal is open
		$('#calculator').on('shown.bs.modal', function () {
			document.addEventListener("keydown", myFunction);
		});

		// Remove keydown event when modal is closed
		$('#calculator').on('hidden.bs.modal', function () {
			document.removeEventListener("keydown", myFunction);
		});
		
		// Kanban Drag
		if($('.kanban-drag-wrap').length > 0) {
			$(".kanban-drag-wrap").sortable({
				connectWith: ".kanban-drag-wrap",
				handle: ".kanban-card",
				placeholder: "drag-placeholder"
			});
		}

		// Timer
		$(".card").each(function () {

			let seconds = 0;
			let timerInterval = null;
			let startedOnce = false;

			const card = $(this);
			const btn = card.find(".timer-btn");
			const icon = btn.find("i");
			const label = btn.find(".label");
			const timeText = btn.find(".time");
			const modalId = btn.data("bs-target");

			function formatTime(sec) {
				let m = String(Math.floor(sec / 60)).padStart(2, "0");
				let s = String(sec % 60).padStart(2, "0");
				return `${m}:${s}`;
			}

			function startTimer() {
				if (timerInterval) return;

				btn.addClass("running");
				icon.removeClass("icon-play").addClass("icon-pause");
				label.text("Pause");

				timerInterval = setInterval(() => {
					seconds++;
					timeText.text(formatTime(seconds));
				}, 1000);
			}

			function pauseTimer() {
				clearInterval(timerInterval);
				timerInterval = null;

				btn.removeClass("running");
				icon.removeClass("icon-pause").addClass("icon-play");
				label.text("Play");
			}

			// ▶ Start timer ONLY first time modal opens
			$(modalId).on("shown.bs.modal", function () {
				if (!startedOnce) {
					startedOnce = true;
					startTimer();
				}
			});

			// ⏯ Toggle play / pause
			btn.on("click", function (e) {

				// If already running → pause (don’t reopen modal)
				if (btn.hasClass("running")) {
					e.preventDefault();
					pauseTimer();
					return;
				}

				// If paused and modal already opened → resume
				if (startedOnce) {
					e.preventDefault();
					startTimer();
				}
			});

		});

	//Increment Decrement Numberes	
	document.querySelectorAll(".quantity-control").forEach(container => {
		const input = container.querySelector(".quantity-input");
		container.querySelector(".add-btn").addEventListener("click", () => {
			input.value = Number(input.value) + 1;
		});
		container.querySelector(".minus-btn").addEventListener("click", () => {
			if (Number(input.value) > 1) input.value = Number(input.value) - 1;
		});
	});


	// Category Slider
	$('.category-slider').each(function () {
		const $slider = $(this);
		if (!$slider.hasClass('slick-initialized')) {
			$slider.slick({
				dots: false,
				infinite: true,
				speed: 2000,
				slidesToShow: 5,
				slidesToScroll: 1,
				autoplay: false,
				arrows: true,
				prevArrow: $('.category-prev'),
				nextArrow: $('.category-next'),
				responsive: [
					{
						breakpoint: 1400,
						settings: { slidesToShow: 4, slidesToScroll: 1 }
					},
					{
						breakpoint: 1200,
						settings: { slidesToShow: 3, slidesToScroll: 1 }
					},
					{
						breakpoint: 992,
						settings: { slidesToShow: 3, slidesToScroll: 1 }
					},
					{
						breakpoint: 768,
						settings: { slidesToShow: 2, slidesToScroll: 1 }
					},
					{
						breakpoint: 576,
						settings: { slidesToShow: 1, slidesToScroll: 1 }
					}
				]
			});
		}
	});

	// Upgrade Slider
	$('.upgrade-slider').each(function () {
		const $slider = $(this);
		if (!$slider.hasClass('slick-initialized')) {
			$slider.slick({
				dots: false,
				infinite: true,
				speed: 2000,
				slidesToShow: 2,
				slidesToScroll: 1,
				autoplay: false,
				arrows: true,
				prevArrow: $('.upgrade-prev'),
				nextArrow: $('.upgrade-next'),
				responsive: [
					{
						breakpoint: 1400,
						settings: { slidesToShow: 2, slidesToScroll: 1 }
					},
					{
						breakpoint: 1200,
						settings: { slidesToShow: 2, slidesToScroll: 1 }
					},
					{
						breakpoint: 992,
						settings: { slidesToShow: 2, slidesToScroll: 1 }
					},
					{
						breakpoint: 768,
						settings: { slidesToShow: 2, slidesToScroll: 1 }
					},
					{
						breakpoint: 576,
						settings: { slidesToShow: 1, slidesToScroll: 1 }
					}
				]
			});
		}
	});

	// Size Tab
	document.addEventListener("click", function(e) {
		const btn = e.target.closest(".size-tab .tag");
		if (!btn) return;
	
		const parent = btn.closest(".size-group");
	
		parent.querySelectorAll(".size-tab").forEach(tab => tab.classList.remove("active"));
	
		btn.closest(".size-tab").classList.add("active");
	});

	// All Sliders
	if ($('.slider-wrapper').length > 0) {
		function initSliders() {
			$('.all-slider, .dinein-slider, .delivery-slider, .takeaway-slider, .table-slider').each(function () {
				const $slider = $(this);
				if (!$slider.hasClass('slick-initialized')) {
					$slider.slick({
						dots: false,
						infinite: true,
						speed: 2000,
						slidesToShow: 3,
						slidesToScroll: 1,
						autoplay: false,
						arrows: false, // disable default arrows
						responsive: [
							{ breakpoint: 1400, settings: { slidesToShow: 3 } },
							{ breakpoint: 1200, settings: { slidesToShow: 2 } },
							{ breakpoint: 992, settings: { slidesToShow: 2 } },
							{ breakpoint: 768, settings: { slidesToShow: 1 } }
						]
					});
				}
			});
		}

		initSliders();

		// Global arrow buttons control the currently active tab’s slider
		$('.all-prev').on('click', function () {
			$('.slider-wrapper .tab-pane.active .slick-slider').slick('slickPrev');
		});

		$('.all-next').on('click', function () {
			$('.slider-wrapper .tab-pane.active .slick-slider').slick('slickNext');
		});

		// Fix Slick when switching tabs
		$('.slider-wrapper a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
			const target = $($(this).attr('data-bs-target'));
			setTimeout(() => {
				target.find('.slick-slider').slick('setPosition');
			}, 100);
		});
	}

	// Accordion Active
	if ($('.menu-item').length > 0) {
	  	$(".menu-item .collapse").on("shown.bs.collapse", function() {
			var $menuItem = $(this).closest(".menu-item");

			// Remove active from all other menu-items
			$(".menu-item.active").not($menuItem).removeClass("active");

			// Add active to this menu-item
			$menuItem.addClass("active");
		});

		// Handle collapse hidden
		$(".menu-item .collapse").on("hidden.bs.collapse", function() {
			var $menuItem = $(this).closest(".menu-item");
			$menuItem.removeClass("active");
		});

		// Optional: mark active for initially open collapse
		$(".menu-item .collapse.show").each(function() {
			$(this).closest(".menu-item").addClass("active");
		});
	}

	// Modal
	if ($('.modal .slick-slider').length > 0) {
		$('.modal').on('shown.bs.modal', function () {
			$('.slick-slider').slick('setPosition');
		});
	}

	// Addon Active
	$(document).on("click", ".addon-item", function () {
		$(this).toggleClass("active");
	});

	if ($('#drag-container').length > 0) {
		const container = document.getElementById('drag-container');
		let draggingElement = null;

		container.addEventListener('dragstart', (e) => {
			draggingElement = e.target.closest('.drag-item');
			e.target.classList.add('dragging');
			// For Firefox support
			e.dataTransfer.setData('text/plain', ''); 
		});

		container.addEventListener('dragend', (e) => {
			e.target.classList.remove('dragging');
			draggingElement = null;
		});

		container.addEventListener('dragover', (e) => {
			e.preventDefault(); // Necessary to allow drop
			const afterElement = getDragAfterElement(container, e.clientY);
			if (afterElement == null) {
				container.appendChild(draggingElement);
			} else {
				container.insertBefore(draggingElement, afterElement);
			}
		});

		// Function to find the element immediately below the mouse cursor
		function getDragAfterElement(container, y) {
			const draggableElements = [...container.querySelectorAll('.drag-item:not(.dragging)')];

			return draggableElements.reduce((closest, child) => {
				const box = child.getBoundingClientRect();
				const offset = y - box.top - box.height / 2;
				if (offset < 0 && offset > closest.offset) {
					return { offset: offset, element: child };
				} else {
					return closest;
				}
			}, { offset: Number.NEGATIVE_INFINITY }).element;
		}
	}


});