odoo.define('hotel.room_management_cancel', function(require) {
    'use strict';

    var FormController = require('web.FormController');
    var core = require('web.core');
    var rpc = require('web.rpc');

    FormController.include({
        events: _.extend({}, FormController.prototype.events, {
            'click .btn-secondary': 'onCancel',
        }),

        onCancel: function (event) {
            event.preventDefault();
            var self = this;

            // Redirect to the list view without saving
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'Rooms',
                res_model: 'room.management',
                view_mode: 'list',
                target: 'current',
            });
        },
    });
});
