$(function () {
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function clear_form_data() {
        $("#order_id").val("");
        $("#order_customer_id").val("");
        $("#order_name").val("");
        $("#order_address").val("");
        $("#order_email").val("");
        $("#order_status").val("");
    }

    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_id").val(res.customer_id);
        $("#order_name").val(res.name);
        $("#order_address").val(res.address);
        $("#order_email").val(res.email);
        $("#order_status").val(res.status);
    }

    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-btn").click(function () {
        $("#flash_message").empty();
        clear_form_data();
        $("#search_results tbody").empty();
    });

    // ****************************************
    // Retrieve an Order by ID
    // ****************************************
    $("#retrieve-btn").click(function () {
        $("#flash_message").empty();

        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Order ID is required");
            return;
        }

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ""
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            clear_form_data();
            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else {
                flash_message("Server error!");
            }
        });
    });

    // ****************************************
    // List/Search Orders
    // ****************************************
    $("#search-btn").click(function () {
        $("#flash_message").empty();

        let customer_id = $("#order_customer_id").val();
        let name = $("#order_name").val();
        let order_status = $("#order_status").val();

        let params = [];
        if (customer_id) {
            params.push(`customer_id=${encodeURIComponent(customer_id)}`);
        }
        if (name) {
            params.push(`name=${encodeURIComponent(name)}`);
        }
        if (order_status) {
            params.push(`status=${encodeURIComponent(order_status)}`);
        }

        let url = "/orders";
        if (params.length > 0) {
            url += "?" + params.join("&");
        }

        let ajax = $.ajax({
            type: "GET",
            url: url,
            contentType: "application/json",
            data: ""
        });

        ajax.done(function (res) {
            $("#search_results tbody").empty();

            let firstOrder = null;

            for (let i = 0; i < res.length; i++) {
                let order = res[i];
                let row = `
                    <tr id="row_${i}">
                        <td>${order.id}</td>
                        <td>${order.customer_id}</td>
                        <td>${order.name}</td>
                        <td>${order.address}</td>
                        <td>${order.email}</td>
                        <td>${order.status}</td>
                    </tr>
                `;
                $("#search_results tbody").append(row);

                if (i === 0) {
                    firstOrder = order;
                }
            }

            if (firstOrder) {
                update_form_data(firstOrder);
            }

            flash_message("Success");
        });

        ajax.fail(function (res) {
            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else {
                flash_message("Server error!");
            }
        });
    });
});