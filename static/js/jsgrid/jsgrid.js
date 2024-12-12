(function($) {
    "use strict";
    $("#basicScenario").jsGrid({
        width: "100%",
        filtering: true,
        editing: true,    // 启用编辑功能
        inserting: true,
        sorting: true,
        paging: true,
        autoload: true,
        pageSize: 15,
        pageButtonCount: 5,
        deleteConfirm: "Do you really want to delete the client?",
        controller: {
            loadData: function (filter) {
                console.log("Filter:", filter);
                return $.ajax({
                    url: '/holdings_data/',  // 后端API的URL
                    method: 'GET',
                    data: filter,  // 传递过滤条件
                    dataType: 'json',
                    success: function (response) {
                        console.log("Data from server:", response);
                    },
                    error: function (xhr, status, error) {
                        console.error("AJAX error:", error);
                    }
                }).then(function (response) {
                    return response.data || [];  // 如果响应格式正确，返回数据
                }).catch(function (xhr, status, error) {
                    console.error("Failed to load data", error);
                    return [];  // 请求失败时返回空数组
                });
            },
            updateItem: function (item) {
                console.log("Sending data to server:", {
                    property_id: item.property_id,
                    Label: item.Label,
                    Note: item.Note,
                    MyBid: item["My Bid"]
                });
    
                return $.ajax({
                    url: '/update_holding_status/',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        property_id: item.property_id,
                        Label: item.Label,
                        Note: item.Note,
                        "My Bid": item["My Bid"]
                    }),
                    dataType: 'json',
                    success: function (response) {
                        console.log("Update success:", response);
    
                        // 成功后重新加载数据
                        $("#basicScenario").jsGrid("loadData");
                    },
                    error: function (xhr, status, error) {
                        console.error("Update error:", error);
                    }
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
                name: "Note",
                type: "text",
                width: 100,
                itemTemplate: function (value, item) {
                    const truncatedValue = value
                        ? value.length > 12
                            ? value.substring(0, 12) + "..."
                            : value
                        : ""; // 如果长度超过12，截取并加"..."
                    const $cell = $("<div>")
                        .text(truncatedValue)
                        .css("cursor", "pointer") // 设置鼠标为手型
                        .attr("title", "Click to edit note") // 鼠标悬停时显示提示
                        .on("click", function (e) {
                            e.stopPropagation(); // 阻止事件冒泡，避免触发表格编辑模式
            
                            // 创建弹出框
                            const $popup = $("<div>")
                                .css({
                                    position: "fixed",
                                    top: "50%",
                                    left: "50%",
                                    transform: "translate(-50%, -50%)",
                                    backgroundColor: "white",
                                    padding: "20px",
                                    boxShadow: "0px 0px 10px rgba(0,0,0,0.5)",
                                    zIndex: 1000
                                });
            
                            const $textarea = $("<textarea>")
                                .css({ width: "100%", height: "100px" })
                                .val(value || "");
            
                            const $saveButton = $("<button>")
                                .text("Save")
                                .css({ marginRight: "10px" })
                                .on("click", function () {
                                    const newValue = $textarea.val();
                                    item.Note = newValue; // 更新表格数据
                                    $cell.text(newValue.substring(0, 12) + "..."); // 更新单元格显示内容
                                    $popup.remove(); // 移除弹出框
            
                                    // 调用 jsGrid 的 updateItem 方法同步更新数据
                                    $("#basicScenario").jsGrid("updateItem", item);
                                });
            
                            const $cancelButton = $("<button>")
                                .text("Cancel")
                                .on("click", function () {
                                    $popup.remove(); // 移除弹出框
                                });
            
                            $popup.append($textarea, $("<div>").append($saveButton, $cancelButton));
                            $("body").append($popup); // 添加到页面
                        });
            
                    return $cell;
                },
                editing: true // 保持编辑功能
            },             
            // 隐藏的字段，不显示在表格中
            { name: "property_user_agreement_id", type: "text", width: 150, editing: false, visible: false },
            {
                name: "Label",
                title: "Status",
                width: 120,
                headerTemplate: function () {
                    const $header = $("<div>").text("Status");
                    const $select = $("<select>")
                        .addClass("status-filter form-select form-select-sm ms-2")
                        .append($("<option>").val("All").text("All"))
                        .append($("<option>").val("Bid").text("Bid"))
                        .append($("<option>").val("Won").text("Won"))
                        .append($("<option>").val("Foreclosed").text("Foreclosed"))
                        .append($("<optgroup>").attr("label", "------"))  // 虚线分隔符
                        .append($("<option>").val("Archived").text("Archived")) // 添加 Archived 选项
                        .on("change", function () {
                            const selectedValue = $(this).val();
                            if (selectedValue === "All") {
                                $("#basicScenario").jsGrid("loadData", { Label: "" });
                                $(".archived-row").hide(); // 隐藏所有 Archived 行
                            } else if (selectedValue === "Archived") {
                                $("#basicScenario").jsGrid("loadData", { Label: "Archived" });
                                $(".archived-row").show(); // 显示所有 Archived 行
                            } else {
                                $("#basicScenario").jsGrid("loadData", { Label: selectedValue });
                                $(".archived-row").hide(); // 隐藏 Archived 行
                            }
                        });
                    $select.val("All"); // 设置默认值为 "All"
                    return $("<div>").append($header).append($select);
                },
                // 编辑时显示下拉框
                editTemplate: function (value) {
                    const $select = $("<select>").addClass("form-select form-select-sm");
                    const options = ["Bid", "Won", "Foreclosed", "Archived"];
                    options.forEach(function (option) {
                        const $option = $("<option>").val(option).text(option);
                        if (option === value) {
                            $option.prop("selected", true); // 设置默认值
                        }
                        $select.append($option);
                    });
        
                    // 将下拉框保存到 this.$select 中
                    this.$select = $select;
                    return $select;
                },
                // 返回编辑时的值
                editValue: function () {
                    return this.$select.val();  // 获取当前选中的值
                }
            },
            { 
                type: "control", 
                width: 150, 
                itemTemplate: function (value, item) {
                    // 创建打开报告的按钮
                    const $reportButton = $("<button>")
                        .addClass("jsgrid")
                        .attr("type", "button")
                        .on("click", function (e) {
                            e.stopPropagation(); // 阻止事件冒泡，防止触发表格行选择或编辑
                            // 点击按钮时打开报告页面
                            window.open(`/report/${item.property_id}`, '_blank');
                        })
                        .on("mouseover", function () {
                            // 鼠标悬停时添加视觉效果
                            $(this).css("background-color", "#f0f0f0");
                        })
                        .on("mouseout", function () {
                            // 鼠标移开时恢复原样
                            $(this).css("background-color", "");
                        });
            
                    // 添加自定义的图标到按钮中
                    $reportButton.append($("<i>").addClass("fa fa-eye")); // 使用 Font Awesome 图标
            
                    // 保留编辑按钮
                    const $editButton = this._createEditButton(item);
            
                    // 返回按钮集合，包含编辑按钮和打开报告按钮
                    return $("<div>").append($editButton).append($reportButton);
                }
            }
            
        ],
    });
    
    
    // 给 Archived 行添加虚线边框
    $(".archived-row").css("border-bottom", "1px dashed #ccc");
    
    

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