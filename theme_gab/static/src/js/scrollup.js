odoo.define('scroll_up.button', function (require) {
'use strict';

    require('web.dom_ready');
    
    var settings = $('#scroll_up_settings');
    
    if(settings.length >= 1) {
	    $.scrollUp({
			scrollName: settings.data('scroll_name') || 'scrollUp', 	// Element ID
	        scrollDistance: settings.data('scroll_distance') || 300, 	// Distance from top/bottom before showing element (px)
	        scrollFrom: settings.data('scroll_from') || 'top', 			// 'top' or 'bottom'
	        scrollSpeed: settings.data('scroll_speed') || 300, 			// Speed back to top (ms)
	        easingType: settings.data('easing_type') || 'linear', 		// Scroll to top easing (see http://easings.net/)
	        animation: settings.data('animation') || 'fade', 			// Fade, slide, none
	        animationSpeed: settings.data('animation_speed') || 200, 	// Animation in speed (ms)
	        scrollTrigger: settings.data('scroll_trigger') || false, 	// Set a custom triggering element. Can be an HTML string or jQuery object
	        scrollTarget: settings.data('scroll_target') || false, 		// Set a custom target element for scrolling to. Can be element or number
	        scrollText: settings.data('scroll_text') || "<i class='fa fa-chevron-circle-up' />", // Text for element, can contain HTML
	        scrollTitle: settings.data('scroll_title') || false, 		// Set a custom <a> title if required. Defaults to scrollText
	        scrollImg: settings.data('scroll_img') || false, 			// Set true to use image
	        activeOverlay: settings.data('active_overlay') || false, 	// Set CSS color to display scrollUp active point, e.g '#00FFFF'
	        zIndex: settings.data('z_index') || 2147483647, 			// Z-Index for the overlay
	    });
    }
});