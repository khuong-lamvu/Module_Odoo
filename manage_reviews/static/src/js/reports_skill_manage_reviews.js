odoo.define("manage_reviews.reports_skill_manage_reviews", function (require) {
    "use strict";
    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var QWeb = core.qweb;
    var ajax = require("web.ajax");
    var _t = core._t;
    // Đường dẫn đến tệp CSS
    var cssPath = "/manage_reviews/static/src/css/survey_templates_result.css";

    // Load tệp CSS
    ajax.loadCSS(cssPath);
    var ReportSkill = AbstractAction.extend({
        contentTemplate: "ReportSkill",
        title: "ReportSkill",
        jsLibs: [
            "/manage_reviews/static/lib/charts/Chart.js",
            "/manage_reviews/static/lib/charts/Chart.bundle.js",
            "/manage_reviews/static/lib/charts/chartjs-plugin-datalabels.js",
            "/web/static/lib/daterangepicker/daterangepicker.js",
            "/web/static/src/legacy/js/libs/daterangepicker.js",
        ],
        events: {
            "click #sort_data": "get_data",
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ["ReportSkill"];
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
                // Xử lý sự kiện khi nhấp vào nút "Xem Đánh giá"
                //                self.$el.on("click", ".btn-view-evaluation", function (ev) {
                //                    var evaluationId = $(ev.currentTarget).data(
                //                        "evaluation-id"
                //                    );
                //                    self.viewEvaluation(evaluationId);
                //                });
            });
        },

        //        viewEvaluation: function (evaluationId) {
        //            // Thực hiện xử lý khi bấm vào nút "Xem Đánh giá" ở đây
        //            console.log("View evaluation with ID: ", evaluationId);
        //            // Gọi phương thức RPC hoặc thực hiện các tác vụ khác để xem chi tiết đánh giá của nhân viên
        //            var url =
        //                "http://localhost:8088/web#id=" +
        //                evaluationId +
        //                "&cids=1&menu_id=284&action=419&model=manage_reviews.evaluation&view_type=form";
        //            window.open(url, "_blank");
        //        },

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
                model: "manage_reviews.evaluation",
                method: "get_phong_ban",
                args: [],
            }).then(function (result) {
                self.result_phong_ban = result[0];
            });
            return $.when(def1);
        },

        render_data: function () {
            var self = this;

            //            var current = new Date();
            //            var weekstart = current.getDate() - current.getDay() + 1;
            //
            //            var monday = new Date(current.setDate(weekstart));
            //            var date = new Date();
            //            var today = date.getDate();
            //            var dayOfTheWeek = date.getDay();
            //            var weekend = date.setDate(today - dayOfTheWeek + 7);
            //            var sunday = new Date(weekend);

            //            // Load select date
            //            self.$('input[name="daterange"]').daterangepicker(
            //                {
            //                    startDate: moment(monday),
            //                    endDate: moment(sunday),
            //                    opens: "left",
            //                    locale: {
            //                        format: "DD/MM/YYYY",
            //                    },
            //                },
            //                function (start, end, label) {
            //                    // Hành động sau khi ngày được chọn
            //                }
            //            );
            //
            //            // Load select project
            //            self.load_list_phong_ban();
            ////
            ////            // Load bieu do tron
            ////            self.load_status_chart();
            ////
            //            // Load  bieu do cot
            //            self.load_bar_chart();
            ////
            //            // Load data
            //            this.get_data();
            self.load_list_phong_ban();

            if (self.result_skill_data) {
                self.load_bar_chart();
                this.get_data();
            }
        },

        //        get_data: function () {
        //            var self = this;
        //            var select_phong_ban = this.$el.find("#select_phong_ban").val();
        ////            var date_range = this.$el.find("#date_range").val();
        ////            var split = date_range.split("-");
        ////            var from_date = split[0].trim();
        ////            var to_date = split[1].trim();
        //
        //            this._rpc({
        //                model: "manage_reviews.evaluation",
        //                method: "get_data_skill",
        ////                args: [from_date, to_date, select_phong_ban],
        //                args: [select_phong_ban],
        //            }).then(function (result) {
        ////                self.result_status_chart = result[0];
        ////                self.result_score_chart = result[1];
        ////                self.result_reviews = result[2];
        //                  self.result_skill_data = result;
        //
        ////                self.load_status_chart();
        //                self.load_bar_chart();
        ////                self.load_reviews();
        //            });
        //        },

        get_data: function () {
            var self = this;
            var select_phong_ban = this.$el.find("#select_phong_ban").val();

            this._rpc({
                model: "manage_reviews.evaluation",
                method: "get_data_skill",
                args: [select_phong_ban],
            }).then(function (result) {
                console.log(result); // Kiểm tra dữ liệu trả về trong Console
                self.result_skill_data = result;
                self.load_bar_chart();
            });
        },

        //Lấy dữ liệu phòng ban
        load_list_phong_ban: function () {
            var self = this;
            this._rpc({
                model: "manage_reviews.evaluation",
                method: "get_phong_ban",
            }).then(function (result) {
                var select_phong_ban =
                    '<option value="" >' +
                    _t("Chọn Phòng/ban...") +
                    "</option>";
                if (result && result.length > 0) {
                    for (var i = 0; i < result.length; i++) {
                        select_phong_ban +=
                            '<option value="' +
                            result[i] +
                            '">' +
                            result[i] +
                            "</option>";
                    }
                }
                self.$("#select_phong_ban").html(select_phong_ban);
            });
        },

        load_bar_chart: function () {
            var self = this;
            var skillData = self.result_skill_data;
            if (this.barChart) {
                this.barChart.destroy();
            }
            if (skillData && Object.keys(skillData).length > 0) {
                var skillLabels = Object.keys(skillData); // Tên kỹ năng
                var employeeNames = Object.values(skillData).reduce(function (
                    names,
                    skill
                ) {
                    return names.concat(skill.employees);
                },
                []); // Danh sách tên nhân viên có kỹ năng

                // Lọc ra danh sách tên nhân viên duy nhất
                var uniqueEmployeeNames = Array.from(new Set(employeeNames));

                var datasets = uniqueEmployeeNames.map(function (employeeName) {
                    var data = skillLabels.map(function (skillLabel) {
                        var skill = skillData[skillLabel];
                        var count = skill.employees.filter(function (name) {
                            return name === employeeName;
                        }).length;
                        return count;
                    });

                    // Tạo màu ngẫu nhiên
                    var randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);

                    return {
                        label: employeeName, // Biểu diễn tên của nhân viên
                        data: data, // Cột chồng lên nhau của nhân viên
                        backgroundColor: randomColor,
                        borderColor: randomColor,
                        borderWidth: 1,
                        stack: "stack1", // Đánh dấu cho cột chồng lên nhau cùng nhau
                    };
                });

                var barData = {
                    labels: skillLabels, // Tên kỹ năng
                    datasets: datasets,
                };

                var ctx = document.getElementById("barChart").getContext("2d");
                this.barChart = new Chart(ctx, {
                    type: "bar",
                    data: barData,
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: "right",
                            },
                        },
                        scales: {
                            x: {
                                stacked: true,
                                grid: {
                                    display: false,
                                },
                                ticks: {
                                    font: {
                                        size: 14,
                                        weight: "bold",
                                    },
                                },
                            },
                            y: {
                                stacked: true,
                                grid: {
                                    color: "#eee",
                                },
                                ticks: {
                                    font: {
                                        size: 14,
                                        weight: "bold",
                                    },
                                    stepSize: 1,
                                    beginAtZero: true,
                                },
                            },
                        },
                    },
                    plugins: {
                        datalabels: {
                            anchor: "end",
                            align: "top",
                            color: "#000000",
                            font: {
                                weight: "bold",
                            },
                            formatter: function (value, context) {
                                return value === 0 ? "" : value;
                            },
                        },
                    },
                });

                // Tạo table cho employees skills matrix
                var table = '<table class="table table-bordered">';
                // Hàng đầu tiên là tiêu đề
                table += "<tr><th></th>";
                uniqueEmployeeNames.forEach(function (employeeName) {
                    table += '<th scope="col">' + employeeName + "</th>";
                });
                table += "</tr>";

                skillLabels.forEach(function (skillLabel) {
                    table += "<tr>";
                    table += '<th scope="row">' + skillLabel + "</th>";
                    uniqueEmployeeNames.forEach(function (employeeName) {
                        var skill = skillData[skillLabel];
                        var skillLevel =
                            skillData[skillLabel].levels[employeeName];
                        var level = ""; // Mức độ kỹ năng tương ứng với số từ 1 đến 5

                        switch (skillLevel) {
                            case "Có thể cải tiến và đào tạo":
                                level =
                                    '<div class="skill-level skill-level-1">1</div>';
                                break;
                            case "Đối ứng khi phát sinh rủi ro":
                                level =
                                    '<div class="skill-level skill-level-2">2</div>';
                                break;
                            case "Làm một mình":
                                level =
                                    '<div class="skill-level skill-level-3">3</div>';
                                break;
                            case "Cần người hỗ trợ":
                                level =
                                    '<div class="skill-level skill-level-4">4</div>';
                                break;
                            case "Không có kinh nghiệm":
                                level =
                                    '<div class="skill-level skill-level-5">5</div>';
                                break;
                            default:
                                level = "";
                                break;
                        }

                        table += "<td>" + level + "</td>";
                    });
                    table += "</tr>";
                });

                // Thêm mô tả các mức độ kỹ năng
                table +=
                    '<tr><td colspan="' +
                    (uniqueEmployeeNames.length + 1) +
                    '">';
                table += "<p><strong>Mô tả các mức độ kỹ năng:</strong></p>";
                table += "<ol>";
                table += "<li>Có thể cải tiến và đào tạo</div></li>";
                table += "<li>Đối ứng khi phát sinh rủi ro</div></li>";
                table += "<li>Làm một mình</div></li>";
                table += "<li>Cần người hỗ trợ</div></li>";
                table += "<li>Không có kinh nghiệm</div></li>";
                table += "</ol>";
                table += "</td></tr>";

                // Đưa table vào container
                $("#employees_skills_matrix").html(table);
            }
        },
    });
    core.action_registry.add("reports_skill_manage_reviews", ReportSkill);
    return ReportSkill;
});
