"use strict";

$(document).ready(function () {
	/* Video Lightbox */
	if (!!$.prototype.simpleLightboxVideo) {
		$('.video').simpleLightboxVideo();
	}

	/*ScrollUp*/
	if (!!$.prototype.scrollUp) {
		$.scrollUp();
	}

	/*Responsive Navigation*/
	$("#nav-mobile").html($("#nav-main").html());
	$("#nav-trigger span").on("click",function() {
		if ($("nav#nav-mobile ul").hasClass("expanded")) {
			$("nav#nav-mobile ul.expanded").removeClass("expanded").slideUp(250);
			$(this).removeClass("open");
		} else {
			$("nav#nav-mobile ul").addClass("expanded").slideDown(250);
			$(this).addClass("open");
		}
	});

	$("#nav-mobile").html($("#nav-main").html());
	$("#nav-mobile ul a").on("click",function() {
		if ($("nav#nav-mobile ul").hasClass("expanded")) {
			$("nav#nav-mobile ul.expanded").removeClass("expanded").slideUp(250);
			$("#nav-trigger span").removeClass("open");
		}
	});

	/* Sticky Navigation */
	if (!!$.prototype.stickyNavbar) {
		$('#header').stickyNavbar();
	}

	$('#content').waypoint(function (direction) {
		if (direction === 'down') {
			$('#header').addClass('nav-solid fadeInDown');
		}
		else {
			$('#header').removeClass('nav-solid fadeInDown');
		}
	});
});

$(window).on('scroll', function() {
	if ($(window).scrollTop() > 100) {
	  $('#header').addClass('sticky');
	} else {
	  $('#header').removeClass('sticky');
	}
});


/* Preloader and animations */
$(window).load(function () { // makes sure the whole site is loaded
	$('#status').fadeOut(); // will first fade out the loading animation
	$('#preloader').delay(350).fadeOut('slow'); // will fade out the white DIV that covers the website.
	$('body').delay(350).css({'overflow-y': 'visible'});

	/* WOW Elements */
	if (typeof WOW == 'function') {
		new WOW().init();
	}

	/* Parallax Effects */
	if (!!$.prototype.enllax) {
		$(window).enllax();
	}
});

// Add this to the end of your site.js file
document.addEventListener('DOMContentLoaded', function() {
    // Debug
    console.log("Navigation active link script running");
    
    // Get current path
    var currentPath = window.location.pathname;
    console.log("Current path:", currentPath);
    
    // Log all nav links to verify selector
    var navLinks = document.querySelectorAll('#nav-main ul li a');
    console.log("Found nav links:", navLinks.length);
    
    // Remove active class from all links
    navLinks.forEach(function(link) {
        link.classList.remove('active');
        console.log("Removed active class from:", link.textContent);
    });
    
    // Add active class to matching link
    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        console.log("Checking link:", href);
        
        // Skip # links except on homepage
        if (href && href.charAt(0) === '#' && currentPath === '/') {
            console.log("Home page hash link:", href);
            if (href === '#banner' || href === '#about') {
                link.classList.add('active');
                console.log("Added active class to:", link.textContent);
            }
        } 
        // Regular links
        else if (href && href.charAt(0) !== '#') {
            if (currentPath === href || (href !== '/' && currentPath.indexOf(href) === 0)) {
                link.classList.add('active');
                console.log("Added active class to:", link.textContent);
            }
        }
    });
});
