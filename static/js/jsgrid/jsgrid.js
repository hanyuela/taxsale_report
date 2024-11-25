(function($) {
    "use strict";
    $("#basicScenario").jsGrid({
        width: "100%",
        filtering: true,
        editing: true,
        inserting: true,
        sorting: true,
        paging: true,
        autoload: true,
        pageSize: 15,
        pageButtonCount: 5,
        deleteConfirm: "Do you really want to delete the client?",
        controller: {
            loadData: function (filter) {
                return $.grep(db.clients, function (client) {
                    return (!filter.Label || client.Label === filter.Label) &&
                           (!filter["Full Address"] || client["Full Address"].indexOf(filter["Full Address"]) > -1) &&
                           (!filter.State || client.State.indexOf(filter.State) > -1) &&
                           (!filter["Auction Authority"] || client["Auction Authority"].indexOf(filter["Auction Authority"]) > -1);
                });
            }
        },
        fields: [
            { name: "Full Address", type: "text", width: 150 },
            { name: "Auction Authority", type: "text", width: 150 },
            { name: "State", type: "text", width: 100 },
            { name: "Amount In Sale", type: "text", width: 120 },
            { name: "Deposit Deadline", type: "text", width: 150 },
            { name: "Auction Start", type: "text", width: 150 },
            { name: "Auction End", type: "text", width: 150 },
            { name: "My Bid", type: "text", width: 100 },
            {
                name: "Label",
                title: "Status",
                width: 120,
                headerTemplate: function () {
                    const $header = $("<div>").text("Status");
                    const $select = $("<select>")
                        .addClass("status-filter form-select form-select-sm ms-2") // 给筛选下拉框添加独立的 class
                        .append($("<option>").val("All").text("All")) // 默认选项
                        .append($("<option>").val("Bid").text("Bid"))
                        .append($("<option>").val("Won").text("Won"))
                        .append($("<option>").val("Foreclosed").text("Foreclosed"))
                        .on("change", function () {
                            const selectedValue = $(this).val();
                            if (selectedValue === "All") {
                                // 清除筛选条件，显示所有数据
                                $("#basicScenario").jsGrid("loadData", { Label: "" });
                            } else {
                                // 按选择的值筛选数据
                                $("#basicScenario").jsGrid("loadData", { Label: selectedValue });
                            }
                        });
    
                    $select.val("All"); // 设置默认值为 "All"
                    return $("<div>").append($header).append($select);
                },
            },
            { type: "control", width: 80 },
        ],
    });
    
    // 初始化加载所有数据
    $("#basicScenario").jsGrid("loadData", {});
    
    // 防止下拉框冲突逻辑
    $(".status-filter").on("click", function (event) {
        event.stopPropagation(); // 阻止事件冒泡到父元素，避免干扰其他功能
    });
    
    
    // 确保加载初始数据
    $("#basicScenario").jsGrid("loadData", {});
    

    $("#sorting-table").jsGrid({
        height:"400px",
        width: "100%",
        autoload: true,
        selecting: false,
        controller: db,
        fields: [
            { name: "Id", type: "text", width: 50 },
            { name: "Product", type: "text", width: 150 },
            { name: "Order Id", type: "text", width: 100 },
            { name: "Price", type: "text", width: 100 },
            { name: "Quantity", type: "text", title: "Quantity", width: 90 },
            { name: "Shipped", type: "text", width: 150 },
            { name: "Total", type: "text", width: 100 },
        ]
    });
    $("#sort").click ( function() {
        var field = $("#sortingField").val();
        $("#sorting-table").jsGrid("sort", field);
    });
    $("#batchDelete").jsGrid({
        width: "100%",
        autoload: true,
        confirmDeleting: false,
        paging: true,
        controller: {
            loadData: function() {
                return db.clients;
            }
        },
        fields: [
            {
                headerTemplate: function() {
                    return $("<button>").attr("type", "button").text("Delete") .addClass("btn btn-danger btn-sm btn-delete mb-0")
                        .click( function () {
                            deleteSelectedItems();
                        });
            },
            itemTemplate: function(_, item) {
                return $("<input>").attr("type", "checkbox")
                        .prop("checked", $.inArray(item, selectedItems) > -1)
                        .on("change", function () {
                            $(this).is(":checked") ? selectItem(item) : unselectItem(item);
                        });
            },
            align: "center",
            width: 80
            },
            { name: "Id", type: "text", width: 50 },
            { name: "Employee Name", type: "Text", width: 150 },
            { name: "Salary", type: "text", width: 100 },
            { name: "Skill", type: "text", width: 60 },
            { name: "Office", type: "text", width: 100 },
            { name: "Hours", type: "text", width: 80 },
            { name: "Experience", type: "text", width: 110 },
        ]
    });
    var selectedItems = [];
    var selectItem = function(item) {
        selectedItems.push(item);
    };
    var unselectItem = function(item) {
        selectedItems = $.grep(selectedItems, function(i) {
            return i !== item;
        });
    };
    var deleteSelectedItems = function() {
        if(!selectedItems.length || !confirm("Are you sure?"))
            return;
        deleteClientsFromDb(selectedItems);
        var $grid = $("#batchDelete");
        $grid.jsGrid("option", "pageIndex", 1);
        $grid.jsGrid("loadData");
        selectedItems = [];
    };
    var deleteClientsFromDb = function(deletingClients) {
        db.clients = $.map(db.clients, function(client) {
            return ($.inArray(client, deletingClients) > -1) ? null : client;
        });
    };
})(jQuery);