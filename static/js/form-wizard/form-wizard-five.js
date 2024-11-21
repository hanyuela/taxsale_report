(function ($) {
  (function (a) {
    a.fn.smartWizard = function (m) {
      var c = a.extend({}, a.fn.smartWizard.defaults, m),
        x = arguments;
      return this.each(function () {
        function C() {
          var e = b.children("div");
          b.children("ul").addClass("anchor");
          e.addClass("content");
          n = a("<div>Loading</div>").addClass("loader");
          k = a("<div></div>").addClass("action-bar");
          p = a("<div></div>").addClass("step-container login-card");
          q = a("<a>" + c.labelNext + "</a>")
            .attr("href", "#")
            .addClass("btn btn-primary");
          r = a("<a>" + c.labelPrevious + "</a>")
            .attr("href", "#")
            .addClass("btn btn-primary");
          s = a("<a>" + c.labelFinish + "</a>")
            .attr("href", "#")
            .addClass("btn btn-primary");
          c.errorSteps &&
            0 < c.errorSteps.length &&
            a.each(c.errorSteps, function (a, b) {
              y(b, !0);
            });
          p.append(e);
          k.append(n);
          b.append(p);
          b.append(k);
          c.includeFinishButton && k.append(s);
          k.append(q).append(r);
          z = p.width();
            function validateStep1(callback) {
              const email = $("#email").val().trim();
              const password = $("#password").val().trim();
              const confirmPassword = $("#confirm_password").val().trim();
          
              // 验证邮箱格式
              if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                  alert("Invalid email format.");
                  return callback(false); // 验证失败，调用回调函数返回 false
              }
              // 验证密码长度
              if (password.length < 6) {
                  alert("Password must be at least 6 characters.");
                  return callback(false);
              }
              // 验证密码是否匹配
              if (password !== confirmPassword) {
                  alert("Passwords do not match.");
                  return callback(false);
              }
          
              // 使用 AJAX 检查邮箱是否已被注册
              $.ajax({
                  url: "/check-email/", // 替换为你的后端 URL
                  type: "POST",
                  contentType: "application/json", // 设置请求的 Content-Type
                  data: JSON.stringify({ email: email }), // 将数据序列化为 JSON 格式
                  headers: {
                      "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val(), // 添加 CSRF 令牌
                  },
                  success: function (response) {
                      if (response.exists) {
                          alert("This email is already registered.");
                          callback(false); // 邮箱已注册，返回 false
                      } else {
                          callback(true); // 邮箱未注册，返回 true
                      }
                  },
                  error: function (xhr, status, error) {
                      console.error("Error:", xhr.responseText); // 打印具体错误信息
                      alert("An error occurred while checking the email. Please try again.");
                      callback(false);
                  },
              });
          }
          
          // 点击按钮时的逻辑
          a(q).click(function () {
              if (a(this).hasClass("buttonDisabled")) return false;
          
              // 在第一步时验证邮箱和密码
              if (h === 0) {
                  validateStep1(function (isValid) {
                      if (isValid) {
                          A(); // 如果验证通过，继续下一步
                      }
                  });
                  return false; // 阻止默认行为，等待回调执行
              }
          
              A();
              return false;
          });
          a(r).click(function () {
            if (a(this).hasClass("buttonDisabled")) return !1;
            B();
            return !1;
          });
          a(s).click(function () {
            if (!a(this).hasClass("buttonDisabled"))
              if (a.isFunction(c.onFinish)) c.onFinish.call(this, a(f));
              else {
                var d = b.parents("form");
                d && d.length && d.submit();
              }
            return !1;
          });
          a(f).bind("click", function (a) {
            if (f.index(this) == h) return !1;
            a = f.index(this);
            1 == f.eq(a).attr("isDone") - 0 && t(a);
            return !1;
          });
          c.keyNavigation &&
            a(document).keyup(function (a) {
              39 == a.which ? A() : 37 == a.which && B();
            });
          D();
          t(h);
        }

        function D() {
          c.enableAllSteps
            ? (a(f, b)
                .removeClass("selected")
                .removeClass("disabled")
                .addClass("done"),
              a(f, b).attr("isDone", 1))
            : (a(f, b)
                .removeClass("selected")
                .removeClass("done")
                .addClass("disabled"),
              a(f, b).attr("isDone", 0));
          a(f, b).each(function (e) {
            a(a(this).attr("href"), b).hide();
            a(this).attr("rel", e + 1);
          });
        }

        function t(e) {
          var d = f.eq(e),
            g = c.contentURL,
            h = d.data("hasContent");
          stepNum = e + 1;
          g && 0 < g.length
            ? c.contentCache && h
              ? w(e)
              : a.ajax({
                  url: g,
                  type: "POST",
                  data: {
                    step_number: stepNum,
                  },
                  dataType: "text",
                  beforeSend: function () {
                    n.show();
                  },
                  error: function () {
                    n.hide();
                  },
                  success: function (c) {
                    n.hide();
                    c &&
                      0 < c.length &&
                      (d.data("hasContent", !0),
                      a(a(d, b).attr("href"), b).html(c),
                      w(e));
                  },
                })
            : w(e);
        }

        function w(e) {
          var d = f.eq(e),
            g = f.eq(h);
          if (
            e != h &&
            a.isFunction(c.onLeaveStep) &&
            !c.onLeaveStep.call(this, a(g))
          )
            return !1;
          c.updateHeight && p.height(a(a(d, b).attr("href"), b).outerHeight());
          if ("slide" == c.transitionEffect)
            a(a(g, b).attr("href"), b).slideUp("fast", function (c) {
              a(a(d, b).attr("href"), b).slideDown("fast");
              h = e;
              u(g, d);
            });
          else if ("fade" == c.transitionEffect)
            a(a(g, b).attr("href"), b).fadeOut("fast", function (c) {
              a(a(d, b).attr("href"), b).fadeIn("fast");
              h = e;
              u(g, d);
            });
          else if ("slideleft" == c.transitionEffect) {
            var k = 0;
            e > h
              ? ((nextElmLeft1 = z + 10),
                (nextElmLeft2 = 0),
                (k = 0 - a(a(g, b).attr("href"), b).outerWidth()))
              : ((nextElmLeft1 =
                  0 - a(a(d, b).attr("href"), b).outerWidth() + 20),
                (nextElmLeft2 = 0),
                (k = 10 + a(a(g, b).attr("href"), b).outerWidth()));
            e == h
              ? ((nextElmLeft1 = a(a(d, b).attr("href"), b).outerWidth() + 20),
                (nextElmLeft2 = 0),
                (k = 0 - a(a(g, b).attr("href"), b).outerWidth()))
              : a(a(g, b).attr("href"), b).animate(
                  {
                    left: k,
                  },
                  "fast",
                  function (e) {
                    a(a(g, b).attr("href"), b).hide();
                  }
                );
            a(a(d, b).attr("href"), b).css("left", nextElmLeft1);
            a(a(d, b).attr("href"), b).show();
            a(a(d, b).attr("href"), b).animate(
              {
                left: nextElmLeft2,
              },
              "fast",
              function (a) {
                h = e;
                u(g, d);
              }
            );
          } else
            a(a(g, b).attr("href"), b).hide(),
              a(a(d, b).attr("href"), b).show(),
              (h = e),
              u(g, d);
          return !0;
        }

        function u(e, d) {
          a(e, b).removeClass("selected");
          a(e, b).addClass("done");
          a(d, b).removeClass("disabled");
          a(d, b).removeClass("done");
          a(d, b).addClass("selected");
          a(d, b).attr("isDone", 1);
          c.cycleSteps ||
            (0 >= h
              ? a(r).addClass("buttonDisabled")
              : a(r).removeClass("buttonDisabled"),
            f.length - 1 <= h
              ? a(q).addClass("buttonDisabled")
              : a(q).removeClass("buttonDisabled"));
          !f.hasClass("disabled") || c.enableFinishButton
            ? a(s).removeClass("buttonDisabled")
            : a(s).addClass("buttonDisabled");
          if (a.isFunction(c.onShowStep) && !c.onShowStep.call(this, a(d)))
            return !1;
        }

        function A() {
          var a = h + 1;
          if (f.length <= a) {
            if (!c.cycleSteps) return !1;
            a = 0;
          }
          t(a);
        }

        function B() {
          var a = h - 1;
          if (0 > a) {
            if (!c.cycleSteps) return !1;
            a = f.length - 1;
          }
          t(a);
        }

        function E(b) {
          a(".content", l).html(b);
          l.show();
        }

        function y(c, d) {
          d
            ? a(f.eq(c - 1), b).addClass("error")
            : a(f.eq(c - 1), b).removeClass("error");
        }
        var b = a(this),
          h = c.selected,
          f = a("ul > li > a[href^='#step-']", b),
          z = 0,
          n,
          l,
          k,
          p,
          q,
          r,
          s;
        k = a(".action-bar", b);
        0 == k.length && (k = a("<div></div>").addClass("action-bar"));
        l = a(".msg-box", b);
        0 == l.length &&
          ((l = a(
            '<div class="msg-box"><div class="content"></div><a href="#" class="close"><i class="icofont icofont-close-line-circled"></i></a></div>'
          )),
          k.append(l));
        a(".close", l).click(function () {
          l.fadeOut("normal");
          return !1;
        });
        if (m && "init" !== m && "object" !== typeof m) {
          if ("showMessage" === m) {
            var v = Array.prototype.slice.call(x, 1);
            E(v[0]);
            return !0;
          }
          if ("setError" === m)
            return (
              (v = Array.prototype.slice.call(x, 1)),
              y(v[0].stepnum, v[0].iserror),
              !0
            );
          a.error("Method " + m + " does not exist");
        } else C();
      });
    };
    a.fn.smartWizard.defaults = {
      selected: 0,
      keyNavigation: !0,
      enableAllSteps: !1,
      updateHeight: !0,
      transitionEffect: "fade",
      contentURL: null,
      contentCache: !0,
      cycleSteps: !1,
      includeFinishButton: !0,
      enableFinishButton: !1,
      errorSteps: [],
      labelNext: "Next",
      labelPrevious: "Previous",
      labelFinish: "Finish",
      onLeaveStep: null,
      onShowStep: null,
      onFinish: null,
    };
  })(jQuery);

  $("#wizard").smartWizard({
    transitionEffect: "slideleft",
    onFinish: onFinishCallback, // 自定义完成回调
  });
  
  function onFinishCallback() {
    // 显示完成消息
    $("#wizard").smartWizard("showMessage", "All step Done.");
  
    // 获取目标表单
    const form = $("#final-form");
    if (form.length) {
      // 确保 CSRF token 存在于表单中
      ensureCsrfToken(form);
  
      // 在提交前动态添加隐藏字段
      addHiddenFieldsFromSteps();
  
      // 延迟提交表单，确保提示显示一段时间
      setTimeout(() => {
        console.log("Submitting form with data:", form.serialize()); // 打印调试信息
        form.submit();
      }, 1000); // 1秒后提交表单
    } else {
      alert("Form not found. Please ensure the form exists."); // 如果表单未找到，显示错误提示
    }
  }
  
  // 确保表单中存在 CSRF token
  function ensureCsrfToken(form) {
    const csrfToken = $("input[name='csrfmiddlewaretoken']");
    if (!csrfToken.length) {
      console.error("CSRF token missing!");
      alert("CSRF token is missing. Cannot proceed.");
      return;
    }
  
    // 确保 CSRF token 在表单中
    if (!$("input[name='csrfmiddlewaretoken']", form).length) {
      form.prepend(csrfToken.clone());
    }
  }
  
  // 动态添加隐藏字段
  function addHiddenFieldsFromSteps() {
    // 清理动态添加的隐藏字段（保留 CSRF token）
    $("#final-form input[type='hidden']").not("input[name='csrfmiddlewaretoken']").remove();
  
    // 获取步骤1的表单数据
    $("#form-step-1 input").each(function () {
      addHiddenField($(this));
    });
  
    // 获取步骤2的表单数据
    $("#form-step-2 input").each(function () {
      if ($(this).val().trim()) {
        addHiddenField($(this));
      }
    });
  
    // 获取步骤3的表单数据（仅选择的项）
    $("#form-step-3 input:checked").each(function () {
      addHiddenField($(this));
    });
  }
  
  // 动态创建隐藏字段
  function addHiddenField(field) {
    const hiddenInput = $("<input>")
      .attr("type", "hidden")
      .attr("name", field.attr("name"))
      .val(field.val());
    $("#final-form").append(hiddenInput);
  }
  
  $(document).ready(function () {
    // 初始化显示第一个步骤
    showStep(1);

    // 绑定 Step 1 的 Next 按钮
    $("#next-step-1").click(function () {
        validateStep1(function (isValid) {
            if (isValid) {
                showStep(2); // 验证通过，跳转到 Step 2
            }
        });
    });

    // 绑定 Step 2 的 Previous 和 Next 按钮
    $("#previous-step-2").click(function () {
        showStep(1); // 返回到 Step 1
    });

    $("#next-step-2").click(function () {
        showStep(3); // 直接跳转到 Step 3，无需验证
    });

    // 绑定 Step 3 的 Previous 和 Next 按钮
    $("#previous-step-3").click(function () {
        showStep(2); // 返回到 Step 2
    });

    $("#next-step-3").click(function () {
        showStep(4); // 直接跳转到 Step 4，无需验证
    });

    // 绑定 Step 4 的 Previous 和 Finish 按钮
    $("#previous-step-4").click(function () {
        showStep(3); // 返回到 Step 3
    });

    $("#finish-step").click(function () {
        onFinishCallback(); // 调用完成的回调函数
    });
});

/**
 * 显示特定步骤
 * @param {Number} stepNum - 要显示的步骤编号
 */
function showStep(stepNum) {
    // 隐藏所有步骤
    $("[id^='step-']").hide();

    // 显示当前步骤
    $("#step-" + stepNum).show();
}

/**
 * 验证 Step 1 的逻辑
 * @param {Function} callback - 验证完成后的回调函数
 */
function validateStep1(callback) {
    const email = $("#email").val().trim();
    const password = $("#password").val().trim();
    const confirmPassword = $("#confirm_password").val().trim();

    // 验证邮箱格式
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        alert("Invalid email format.");
        return callback(false);
    }
    // 验证密码长度
    if (password.length < 6) {
        alert("Password must be at least 6 characters.");
        return callback(false);
    }
    // 验证密码是否匹配
    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return callback(false);
    }

    // 使用 AJAX 检查邮箱是否已注册
    $.ajax({
        url: "/check-email/", // 替换为你的后端 URL
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ email: email }),
        headers: {
            "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function (response) {
            if (response.exists) {
                alert("This email is already registered.");
                callback(false);
            } else {
                callback(true);
            }
        },
        error: function (xhr) {
            console.error("Error:", xhr.responseText);
            alert("An error occurred while checking the email. Please try again.");
            callback(false);
        },
    });
}

/**
 * 完成步骤的逻辑
 */
function onFinishCallback() {
    const form = $("#final-form");
    if (form.length) {
        // 确保 CSRF token 存在于表单中
        ensureCsrfToken(form);

        // 在提交前动态添加隐藏字段
        addHiddenFieldsFromSteps();

        // 显示提交成功提示
        showSubmissionMessage("CONGRATULATIONS, ALL STEP DONE!");

        // 延迟 2 秒后提交表单
        setTimeout(() => {
            console.log("Submitting form with data:", form.serialize());
            form.submit();
        }, 2000); // 2 秒延迟
    } else {
        alert("Form not found. Please ensure the form exists.");
    }
}

/**
 * 确保表单中存在 CSRF token
 */
function ensureCsrfToken(form) {
    const csrfToken = $("input[name='csrfmiddlewaretoken']");
    if (!csrfToken.length) {
        console.error("CSRF token missing!");
        alert("CSRF token is missing. Cannot proceed.");
        return;
    }

    // 确保 CSRF token 在表单中
    if (!$("input[name='csrfmiddlewaretoken']", form).length) {
        form.prepend(csrfToken.clone());
    }
}

/**
 * 动态添加隐藏字段
 */
function addHiddenFieldsFromSteps() {
    // 清理动态添加的隐藏字段（保留 CSRF token）
    $("#final-form input[type='hidden']").not("input[name='csrfmiddlewaretoken']").remove();

    // 获取步骤1的表单数据
    $("#form-step-1 input").each(function () {
        addHiddenField($(this));
    });

    // 获取步骤2的表单数据
    $("#form-step-2 input").each(function () {
        addHiddenField($(this));
    });

    // 获取步骤3的表单数据
    $("#form-step-3 input:checked").each(function () {
        addHiddenField($(this));
    });
}

/**
 * 动态创建隐藏字段
 */
function addHiddenField(field) {
    const hiddenInput = $("<input>")
        .attr("type", "hidden")
        .attr("name", field.attr("name"))
        .val(field.val());
    $("#final-form").append(hiddenInput);
}

/**
 * 显示提交成功消息
 * @param {String} message - 要显示的消息
 */
  function showSubmissionMessage(message) {
    const messageDiv = $("<div>")
        .text(message)
        .css({
            position: "fixed",
            top: "20px", // 右上角位置
            right: "20px",
            background: "green",
            color: "white",
            padding: "10px 15px", // 缩小的内边距
            "border-radius": "8px",
            "font-size": "16px", // 缩小字体
            "text-align": "center",
            "z-index": 1000,
            "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)", // 添加阴影
        });

    $("body").append(messageDiv);

    // 2 秒后移除提示
    setTimeout(() => {
        messageDiv.fadeOut(500, function () {
            $(this).remove();
        });
    }, 2000);
}

})(jQuery);
