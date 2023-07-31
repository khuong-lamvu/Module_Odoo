odoo.define("bugs_management.dashboard_bugs_management", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var ajax = require("web.ajax");
    var _t = core._t;

    function getRandomColor() {
        var letters = "0123456789ABCDEF";
        var color = "#";
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    var DashboardBugs = AbstractAction.extend({
        contentTemplate: "DashboardBugs",
        title: _t("DashboardBugs"),
        jsLibs: [
            "/bugs_management/static/lib/charts/Chart.js",
            "/bugs_management/static/lib/charts/Chart.bundle.js",
            "/bugs_management/static/lib/charts/chartjs-plugin-datalabels.js",
            "/web/static/lib/daterangepicker/daterangepicker.js",
            "/web/static/src/legacy/js/libs/daterangepicker.js",
        ],
        events: {
            "click #sort_data": "onSortDataClick", // Thay đổi sự kiện để xử lý khi nhấp vào nút "Lọc dữ liệu"
        },

        // Hàm ánh xạ giá trị trạng thái
        mapStatus: function (status) {
            switch (status) {
                case "hoanthanh":
                    return "Hoàn thành";
                case "dangxuly":
                    return "Đang xử lý";
                case "choxuly":
                    return "Chờ xử lý";
                case "huy":
                    return "Hủy";
                default:
                    return status;
            }
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ["DashboardBugs"];
            this.datatable = {
                total_forecast: 0, // Thêm thuộc tính total_forecast để lưu tổng số lỗi
                completed_errors: 0, // Thêm thuộc tính completed_errors để lưu tổng số lỗi hoàn thành
                incomplete_errors: 0, // Thêm thuộc tính incomplete_errors để lưu tổng số lỗi chưa hoàn thành
                cancel_errors: 0, // Thêm thuộc tính cancel_errors để lưu tổng số lỗi đã hủy
            };
        },

        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },

        start: function () {
            var self = this;
            return this._super().then(function () {
                self.render_data();
            });
        },

        fetch_data: function () {
            var self = this;
            var current = new Date();
            var weekstart = current.getDate() - current.getDay() + 1;
            var weekend = weekstart + 6;
            var monday = new Date(current.setDate(weekstart))
                .toISOString()
                .slice(0, 10);
            const date = new Date();
            const today = date.getDate();
            const dayOfTheWeek = date.getDay();
            const newDate = date.setDate(today - dayOfTheWeek + 7);
            var sunday = new Date(newDate).toISOString().slice(0, 10);

            var def1 = this._rpc({
                model: "bugs_management.project_error",
                method: "get_select_project_error",
                args: [],
            }).then(function (result) {
                self.project_errors_result = result;
            });
            return $.when(def1);
        },

        render_data: function () {
            var self = this;
            var current = new Date();
            var weekstart = current.getDate() - current.getDay() + 1;
            var monday = new Date(current.setDate(weekstart));
            var date = new Date();
            var today = date.getDate();
            var dayOfTheWeek = date.getDay();
            var weekend = date.setDate(today - dayOfTheWeek + 7);
            var sunday = new Date(weekend);

            // Load select date
            self.$('input[name="daterange"]').daterangepicker(
                {
                    startDate: moment(monday),
                    endDate: moment(sunday),
                    opens: "left",
                    locale: {
                        format: "DD/MM/YYYY",
                    },
                },
                function (start, end, label) {
                    // Hành động sau khi ngày được chọn
                    // Không thực hiện thống kê tự động ở đây
                }
            );

            // Load select project
            self.load_list_project_error();

            // Load data
            // Không thực hiện thống kê tự động ở đây
        },

        onSortDataClick: function () {
            // Hàm xử lý khi nhấp vào nút "Lọc dữ liệu"
            this.get_data();
        },

        get_data: function () {
            var self = this;
            var select_project_error = this.$el
                .find("#select_project_error")
                .val();
            var date_range = this.$el.find("#date_range").val();
            var split = date_range.split("-");
            var from_date = split[0].trim();
            var to_date = split[1].trim();

            console.log("Select Project Error: ", select_project_error);
            console.log("From Date: ", from_date);
            console.log("To Date: ", to_date);

            // Gọi phương thức để lấy tổng số lỗi
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_project_error_bug_count",
                args: [select_project_error, from_date, to_date],
            }).then(function (bugCount) {
                self.datatable.total_forecast = bugCount;
                self.display_bug_count();
            });

            // Gọi phương thức để lấy số lượng lỗi đã hoàn thành
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_completed_errors_count",
                args: [select_project_error, from_date, to_date],
            }).then(function (completedErrorCount) {
                self.datatable.completed_errors = completedErrorCount;
                self.display_completed_errors_count();
            });

            // Gọi phương thức để lấy số lượng lỗi chưa hoàn thành (bao gồm số lỗi của dự án đang chờ xử lý và số lỗi của dự án đang xử lý)
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_incomplete_errors_count",
                args: [select_project_error, from_date, to_date],
            }).then(function (incompleteErrorCount) {
                self.datatable.incomplete_errors = incompleteErrorCount;
                self.display_incomplete_errors_count();
            });

            // Gọi phương thức để lấy số lượng lỗi đã hủy
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_cancel_errors_count",
                args: [select_project_error, from_date, to_date],
            }).then(function (cancelErrorCount) {
                self.datatable.cancel_errors = cancelErrorCount;
                self.display_cancel_errors_count();
            });

            // Gọi phương thức để lấy danh sách nhân viên và số lỗi của họ
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_employee_bug_count", // Tên phương thức lấy dữ liệu nhân viên và số lỗi
                args: [select_project_error, from_date, to_date],
            }).then(function (employeeData) {
                // Gọi phương thức vẽ biểu đồ cột với dữ liệu nhân viên và số lỗi của họ
                self.draw_employee_chart(employeeData);
                console.log("List employee:  ", employeeData);
            });

            // Gọi phương thức để lấy thống kê số lỗi theo chức năng
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_functionality_bug_count",
                args: [select_project_error, from_date, to_date],
            }).then(function (functionalityData) {
                self.draw_functionality_chart(functionalityData);
            });

            // Gọi phương thức để lấy thông tin lỗi từ backend
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_error_data", // Thay đổi thành tên phương thức lấy thông tin lỗi
                args: [select_project_error, from_date, to_date],
            }).then(function (errorData) {
                console.log("Error Data from Python:", errorData); // Thêm dòng này để ghi thông tin vào bảng điều khiển trình duyệt
                // Hiển thị thông tin lỗi trong bảng
                self.display_error_data(errorData);
            });
        },

        load_list_project_error: function () {
            var self = this;
            this._rpc({
                model: "bugs_management.project_error",
                method: "get_select_project_error",
            }).then(function (result) {
                var select_project_error =
                    '<option value="" >' +
                    _t("Chọn dự án lỗi...") +
                    "</option>";
                if (result && result.length > 0) {
                    for (var i = 0; i < result.length; i++) {
                        select_project_error +=
                            '<option value="' +
                            result[i].id +
                            '">' +
                            result[i].name +
                            "</option>";
                    }
                }
                self.$("#select_project_error").html(select_project_error);
            });
        },

        display_bug_count: function () {
            var self = this;
            // Render data to info-box elements
            var $title = this.$(".info-box .title");
            $title.text(this.datatable.total_forecast);
        },

        display_completed_errors_count: function () {
            var self = this;
            // Render data to info-box elements
            var $completedTitle = this.$(".info-box .completed-title");
            $completedTitle.text(this.datatable.completed_errors);
        },

        display_incomplete_errors_count: function () {
            var self = this;
            // Render data to info-box elements
            var $incompleteTitle = this.$(".info-box .incomplete-title");
            $incompleteTitle.text(this.datatable.incomplete_errors);
        },

        display_cancel_errors_count: function () {
            var self = this;
            // Render data to info-box elements
            var $cancelTitle = this.$(".info-box .cancel-title");
            $cancelTitle.text(this.datatable.cancel_errors);
        },

        draw_employee_chart: function (employeeData) {
            var self = this;
            var labels = [];
            var data = [];
            if (this.error_chart) {
                this.error_chart.destroy();
            }
            // Tạo danh sách tên nhân viên và số lỗi tương ứng
            for (var i = 0; i < employeeData.length; i++) {
                labels.push(employeeData[i].employee_name);
                data.push(employeeData[i].bug_count);
            }

            var backgroundColors = [];
            var borderColors = [];
            for (var i = 0; i < data.length; i++) {
                // Sinh màu ngẫu nhiên cho từng dữ liệu
                var bgColor = getRandomColor();
                var borderColor = getRandomColor();
                backgroundColors.push(bgColor);
                borderColors.push(borderColor);
            }

            // Vẽ biểu đồ cột
            var ctx = document.getElementById("error_chart").getContext("2d");
            this.error_chart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Số lỗi phụ trách",
                            data: data,
                            backgroundColor: backgroundColors,
                            borderColor: borderColors,
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
            });
        },

        draw_functionality_chart: function (functionalityData) {
            var self = this;
            var labels = [];
            var data = [];
            if (this.functionality_chart) {
                this.functionality_chart.destroy();
            }
            // Tạo danh sách tên chức năng và số lỗi tương ứng
            for (var i = 0; i < functionalityData.length; i++) {
                labels.push(functionalityData[i].functionality_name);
                data.push(functionalityData[i].bug_count);
            }

            var backgroundColors = [];
            var borderColors = [];
            for (var i = 0; i < data.length; i++) {
                // Sinh màu ngẫu nhiên cho từng dữ liệu
                var bgColor = getRandomColor();
                var borderColor = getRandomColor();
                backgroundColors.push(bgColor);
                borderColors.push(borderColor);
            }

            // Vẽ biểu đồ tròn
            var ctx = document
                .getElementById("functionality_chart")
                .getContext("2d");
            this.functionality_chart = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            data: data,
                            backgroundColor: backgroundColors,
                            borderColor: borderColors,
                            borderWidth: 1,
                        },
                    ],
                },
            });
        },

        display_error_data: function (errorData) {
            var $tableBody = this.$("#tbody_bugs_management_all");
            $tableBody.empty();

            if (errorData && Array.isArray(errorData)) {
                for (var i = 0; i < errorData.length; i++) {
                    var $row = $("<tr>");
                    $row.append(
                        ' <td class="align-middle text-center">' +
                            (errorData[i].name || "") +
                            "</td>"
                    );
                    $row.append(
                        ' <td class="align-middle text-center">' +
                            (errorData[i].functionality || "") +
                            "</td>"
                    );
                    $row.append(
                        ' <td class="align-middle text-center">' +
                            (errorData[i].date_created || "") +
                            "</td>"
                    );
                    $row.append(
                        ' <td class="align-middle text-center">' +
                            this.mapStatus(errorData[i].status) +
                            "</td>"
                    );
                    $tableBody.append($row);
                }
            }
        },
    });

    core.action_registry.add("dashboard_bugs_management", DashboardBugs);
    return DashboardBugs;
});
