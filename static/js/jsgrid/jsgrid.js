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
                // 获取原始数据
                const originalItem = $("#basicScenario").jsGrid("option", "data").find(i => i.property_id === item.property_id);
            
                // 找出被修改的字段
                const modifiedFields = {};
                Object.keys(item).forEach(key => {
                    if (item[key] !== originalItem[key]) {
                        modifiedFields[key] = item[key];
                    }
                });
            
                // 如果没有修改任何字段，直接返回
                if (Object.keys(modifiedFields).length === 0) {
                    console.log("No changes detected");
                    return Promise.resolve();
                }
            
                // 添加 `property_id` 到修改的字段中，作为标识符
                modifiedFields.property_id = item.property_id;
            
                console.log("Modified fields:", modifiedFields);
            
                // 原始字段的数据提交
                if (modifiedFields.Label || modifiedFields.Note || modifiedFields["My Bid"]) {
                    console.log("Sending data to update_holding_status:", {
                        property_id: item.property_id,
                        Label: modifiedFields.Label,
                        Note: modifiedFields.Note,
                        MyBid: modifiedFields["My Bid"]
                    });
            
                    $.ajax({
                        url: '/update_holding_status/', // 原接口
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            property_id: item.property_id,
                            Label: modifiedFields.Label,
                            Note: modifiedFields.Note,
                            "My Bid": modifiedFields["My Bid"]
                        }),
                        dataType: 'json',
                        success: function (response) {
                            console.log("Update holding status success:", response);
            
                            // 成功后重新加载数据
                            $("#basicScenario").jsGrid("loadData");
                        },
                        error: function (xhr, status, error) {
                            console.error("Update holding status error:", error);
                        }
                    });
                }
            
                // 保存新增字段到 /save_user_input/，仅提交修改的字段
                const saveUserInputFields = [
                    "Address", 
                    "City", 
                    "Zip", 
                    "Auction Authority", 
                    "State", 
                    "Amount In Sale", 
                    "Deposit Deadline", 
                    "Auction Start", 
                    "Auction End", 
                    "Batch Number", 
                    "Sort No", 
                    "Bankruptcy Flag", 
                    "Parcel Number", 
                    "Property Class", 
                    "Tax Overdue", 
                    "Accessed Land Value", 
                    "Accessed Improvement Value", 
                    "Total Assessed Value", 
                    "Tax Amount Annual", 
                    "Zillow Link", 
                    "Redfin Link", 
                    "Market Land Value", 
                    "Market Improvement Value", 
                    "Total Market Value", 
                    "Year Built", 
                    "Lot Size (sqft)", 
                    "Lot Size (acres)", 
                    "Building Size (sqft)", 
                    "Bedroom Number", 
                    "Bathroom Number", 
                    "Nearby Schools", 
                    "Walk Score", 
                    "Transit Score", 
                    "Bike Score", 
                    "Environmental Hazard Status", 
                    "Flood Status", 
                    "Flood Risk", 
                    "Latest Sale Date", 
                    "Latest Sale Price"
                ];
                
                const userInputData = { property_id: item.property_id };
            
                saveUserInputFields.forEach(field => {
                    if (modifiedFields[field] !== undefined) {
                        const fieldName = field === "Address" ? "street_address" : field.toLowerCase().replace(/ /g, "_");
                        userInputData[fieldName] = modifiedFields[field];
                    }
                });
                
            
                if (Object.keys(userInputData).length > 1) { // 确保除了 property_id 外有其他字段
                    console.log("Sending data to save_user_input:", userInputData);
            
                    return $.ajax({
                        url: '/save_user_input/', // 新接口
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(userInputData),
                        dataType: 'json',
                        success: function (response) {
                            console.log("Save user input success:", response);
            
                            // 成功后重新加载数据
                            $("#basicScenario").jsGrid("loadData");
                        },
                        error: function (xhr, status, error) {
                            console.error("Save user input error:", error);
                        }
                    });
                } else {
                    console.log("No fields to save for user input");
                    return Promise.resolve();
                }
            }            
        },
        fields: [
            {
                name: "Address",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Address"];
                    const color = isUserInput ? "#2b5f60" : ""; // 如果是用户输入，设置文本颜色为绿色
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "City",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["City"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Zip",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Zip"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Auction Authority",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Auction Authority"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "State",
                type: "text",
                width: 100,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["State"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color) // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Amount In Sale",
                type: "text",
                width: 120,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Amount In Sale"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Deposit Deadline",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Deposit Deadline"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Auction Start",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Auction Start"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Auction End",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Auction End"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            //新增字段
            {
                name: "Batch Number",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Batch Number"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Sort No",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Sort No"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Bankruptcy Flag",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Bankruptcy Flag"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value ? "Yes" : "No")
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Parcel Number",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Parcel Number"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Property Class",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Property Class"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Tax Overdue",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Tax Overdue"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Accessed Land Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Accessed Land Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Accessed Improvement Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Accessed Improvement Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Total Assessed Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Total Assessed Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Tax Amount Annual",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Tax Amount Annual"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Zillow Link",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Zillow Link"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Redfin Link",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Redfin Link"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Market Land Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Market Land Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Market Improvement Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Market Improvement Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Total Market Value",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Total Market Value"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Year Built",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Year Built"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Lot Size (sqft)",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Lot Size (sqft)"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Lot Size (acres)",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Lot Size (acres)"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Building Size (sqft)",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Building Size (sqft)"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Bedroom Number",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Bedroom Number"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Bathroom Number",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Bathroom Number"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Nearby Schools",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Nearby Schools"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Walk Score",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Walk Score"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Transit Score",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Transit Score"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Bike Score",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Bike Score"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Environmental Hazard Status",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Environmental Hazard Status"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Flood Status",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Flood Status"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Flood Risk",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Flood Risk"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Latest Sale Date",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Latest Sale Date"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            {
                name: "Latest Sale Price",
                type: "text",
                width: 150,
                itemTemplate: function(value, item) {
                    const isUserInput = item.is_user_input && item.is_user_input["Latest Sale Price"];
                    const color = isUserInput ? "#2b5f60" : "";
                    const $cell = $("<div>")
                        .text(value)
                        .css("color", color)  // 仅设置文本颜色
                        .css("background-color", ""); // 保持背景色为白色或默认色
                    return $cell;
                }
            },
            //新增结束
            
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
                                .val(value || "")
                                .on("input", function() {
                                    const currentLength = $(this).val().length;
                                    if (currentLength > 1000) {
                                        // 如果字符超过1000，显示提示信息
                                        $("#charLimitWarning").show();
                                    } else {
                                        $("#charLimitWarning").hide();
                                    }
                                });
            
                            const $saveButton = $("<button>")
                                .text("Save")
                                .css({ marginRight: "10px" })
                                .on("click", function () {
                                    const newValue = $textarea.val();
            
                                    if (newValue.length > 1000) {
                                        // alert("Note cannot exceed 1000 characters.");
                                        return;
                                    }
            
                                    // 调用 $.ajax() 发送数据到后台更新
                                    $.ajax({
                                        url: '/update_holding_status/', // 原接口
                                        method: 'POST',
                                        contentType: 'application/json',
                                        data: JSON.stringify({
                                            property_id: item.property_id, // 保持当前任务的 ID
                                            Label: item.Label, // 保持其他需要传递的字段
                                            Note: newValue, // 更新的 Note 字段
                                            "My Bid": item["My Bid"] // 如果需要更新 My Bid 字段
                                        }),
                                        dataType: 'json',
                                        success: function (response) {
                                            console.log("Update holding status success:", response);
                                            
                                            // 更新后刷新表格
                                            $("#basicScenario").jsGrid("loadData");
                                            $popup.remove(); // 关闭弹出框
                                        },
                                        error: function (xhr, status, error) {
                                            console.error("Update holding status error:", error);
                                        }
                                    });
                                });
            
                            const $cancelButton = $("<button>")
                                .text("Cancel")
                                .on("click", function () {
                                    $popup.remove(); // 移除弹出框
                                });
            
                            // 添加字符限制提示信息
                            const $charLimitWarning = $("<div>")
                                .attr("id", "charLimitWarning")
                                .css({
                                    color: "red",
                                    fontSize: "12px",
                                    display: "none" // 默认隐藏
                                })
                                .text("Note cannot exceed 1000 characters.");
            
                            $popup.append($textarea, $charLimitWarning, $("<div>").append($saveButton, $cancelButton));
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
        onRefreshed: function () {
            const grid = $("#basicScenario");
            const headerRow = grid.find(".jsgrid-header-row"); // 找到表头行
        
            // 如果 headerRow 存在，则绑定拖拽事件
            if (headerRow.length) {
                const headers = headerRow.children("th"); // 获取所有表头列
        
                // 解绑旧事件，避免重复绑定
                headers.off("dragstart dragover dragleave drop dragend");
        
                headers.each(function (index) {
                    $(this).attr("draggable", "true"); // 开启拖拽
                    $(this).data("index", index); // 保存列索引
        
                    // 绑定拖拽事件
                    $(this)
                        .on("dragstart", function (e) {
                            e.originalEvent.dataTransfer.setData("fromIndex", index); // 保存拖动的起始索引
                            $(this).addClass("dragging");
                        })
                        .on("dragover", function (e) {
                            e.preventDefault(); // 必须阻止默认事件，才能触发 drop
                            $(this).addClass("drag-over");
                        })
                        .on("dragleave", function () {
                            $(this).removeClass("drag-over");
                        })
                        .on("drop", function (e) {
                            e.preventDefault();
                            $(this).removeClass("drag-over");
        
                            const fromIndex = parseInt(e.originalEvent.dataTransfer.getData("fromIndex"), 10); // 获取起始索引
                            const toIndex = $(this).data("index"); // 获取目标索引
        
                            // 如果索引不同，则交换列
                            if (fromIndex !== toIndex) {
                                swapFields(fromIndex, toIndex);
                            }
                        })
                        .on("dragend", function () {
                            $(this).removeClass("dragging");
                        });
                });
            }
        }
        
    });
    function swapFields(fromIndex, toIndex) {
        const grid = $("#basicScenario");
    
        // 获取当前的 fields 配置
        const fields = grid.jsGrid("option", "fields");
    
        // 交换 fields 中的列配置
        const temp = fields[fromIndex];
        fields[fromIndex] = fields[toIndex];
        fields[toIndex] = temp;
    
        // 确保每个字段都有完整的配置（例如 visible）
        fields.forEach(field => {
            if (field.visible === undefined) {
                field.visible = true; // 设置默认可见性
            }
        });
    
        // 更新 jsGrid 配置并重新渲染表格
        grid.jsGrid("option", "fields", fields);
    
        // 加载最新数据
        grid.jsGrid("loadData"); // 替换 grid.jsGrid("refresh");
    
        console.log(`Swapped columns: ${fromIndex} ↔ ${toIndex}`);
    }
    
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