odoo.define("manage_reviews.dashboard_manage_reviews", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var QWeb = core.qweb;
    var ajax = require("web.ajax");
    var _t = core._t;

    var DashboardReviews = AbstractAction.extend({
        contentTemplate: "DashboardReviews",
        title: "DashboardReviews",
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
            this.dashboards_templates = ["DashboardReviews"];
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
                self.$el.on("click", ".btn-view-evaluation", function (ev) {
                    var evaluationId = $(ev.currentTarget).data(
                        "evaluation-id"
                    );
                    self.viewEvaluation(evaluationId);
                });
            });
        },

        viewEvaluation: function (evaluationId) {
            // Thực hiện xử lý khi bấm vào nút "Xem Đánh giá" ở đây
            console.log("View evaluation with ID: ", evaluationId);
            // Gọi phương thức RPC hoặc thực hiện các tác vụ khác để xem chi tiết đánh giá của nhân viên
            var url =
                "http://localhost:8088/web#id=" +
                evaluationId +
                "&cids=1&menu_id=284&action=419&model=manage_reviews.evaluation&view_type=form";
            window.open(url, "_blank");
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
                }
            );

            // Load select project
            self.load_list_phong_ban();

            // Load bieu do tron
            self.load_status_chart();

            // Load  bieu do cot
            self.load_bar_chart();

            // Load data
            this.get_data();
        },

        get_data: function () {
            var self = this;
            var select_phong_ban = this.$el.find("#select_phong_ban").val();
            var date_range = this.$el.find("#date_range").val();
            var split = date_range.split("-");
            var from_date = split[0].trim();
            var to_date = split[1].trim();

            this._rpc({
                model: "manage_reviews.evaluation",
                method: "get_data_reviews",
                args: [from_date, to_date, select_phong_ban],
            }).then(function (result) {
                self.result_status_chart = result[0];
                self.result_score_chart = result[1];
                self.result_reviews = result[2];

                self.load_status_chart();
                self.load_bar_chart();
                self.load_reviews();
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

        load_status_chart: function () {
            var self = this;

            // Xóa biểu đồ cũ
            if (self.status_chart) {
                self.status_chart.destroy();
            }

            // Kiểm tra xem biến self.result_status_chart có giá trị hay không
            if (
                self.result_status_chart &&
                self.result_status_chart.length > 0
            ) {
                var yeu = 0;
                var trung_binh = 0;
                var kha = 0;
                var gioi = 0;

                for (var i = 0; i < self.result_status_chart.length; i++) {
                    yeu = self.result_status_chart[i].yeu;
                    trung_binh = self.result_status_chart[i].trung_binh;
                    kha = self.result_status_chart[i].kha;
                    gioi = self.result_status_chart[i].gioi;
                }

                self.$("#card_chart_status").css("display", "block");

                if (yeu + trung_binh + kha + gioi) {
                    self.$("#status_chart_legends").css("display", "block");
                } else {
                    self.$("#status_chart_legends").css("display", "none");
                }

                var status_chart = this.$el.find("#status_chart");
                if (status_chart.length) {
                    var status_chart = new Chart(status_chart, {
                        type: "doughnut",
                        data: {
                            indexLabelFontColor: "white",
                            labels: ["Yếu", "Trung bình", "Khá", "Tốt"],
                            datasets: [
                                {
                                    data: [yeu, trung_binh, kha, gioi],
                                    backgroundColor: [
                                        "#8064a2",
                                        "#4f81bd",
                                        "#ed7d31",
                                        "#599a66",
                                    ],
                                },
                            ],
                        },
                        options: {
                            plugins: {
                                datalabels: {
                                    display: false,
                                },
                            },
                            responsive: true,
                            maintainAspectRatio: true,
                            legend: {
                                position: "right",
                                display: false,
                                labels: {
                                    fontColor: "black",
                                },
                            },
                            title: {
                                fontSize: 16,
                                fontColor: "black",
                                display: false,
                                text: "Nhiệm vụ trong tuần",
                            },
                        },
                    });
                }

                self.status_chart = status_chart;
            } else {
                console.log("Không có dữ liệu result_status_chart.");
            }
        },

        load_bar_chart: function () {
            var self = this;
            if (this.kpi_chart) {
               this.kpi_chart.destroy();
            }
            if (self.result_score_chart && self.result_score_chart.length > 0) {
                var labels = [];
                var kpiScores = [];

                for (var i = 0; i < self.result_score_chart.length; i++) {
                    var item = self.result_score_chart[i];
                    labels.push(item["ten_nhansu"]);
                    kpiScores.push(item["kpi_score"]);
                }

                var ctx = document.getElementById("kpi_chart").getContext("2d");
                // Xóa biểu đồ cũ nếu đã tồn tại


                this.kpi_chart = new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: "Điểm KPI",
                                data: kpiScores,
                                backgroundColor: "rgba(54, 162, 235, 0.5)",
                                borderColor: "rgba(54, 162, 235, 1)",
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
            }
        },

        load_reviews: function () {
            var self = this;
            var tbody_manage_reviews_all = "";

            var date_range = this.$el.find("#date_range").val();
            var split = date_range.split("-");
            var from_date = split[0].trim();
            var to_date = split[1].trim();

            from_date = new Date(
                parseInt(from_date.slice(6)),
                parseInt(from_date.slice(3, 5)),
                parseInt(from_date.slice(0, 2))
            );
            to_date = new Date(
                parseInt(to_date.slice(6)),
                parseInt(to_date.slice(3, 5)),
                parseInt(to_date.slice(0, 2))
            );

            if (self.result_reviews && self.result_reviews.length) {
                for (var i = 0; i < self.result_reviews.length; i++) {
                    var stt = i + 1;
                    var str_tr = "<tr>";

                    let day_reception = null;
                    let date_deadline = null;

                    if (self.result_reviews[i]) {
                        // Nhân viên
                        str_tr +=
                            ' <td class="align-middle text-left">' +
                            self.result_reviews[i].ten_nhansu +
                            "</td>";

                        // Điểm KPI (Hiện tại)
                        str_tr +=
                            ' <td class="align-middle text-center">' +
                            self.result_reviews[i].kpi_score +
                            "</td>";
                        // Điểm KPI (6 tháng trước)
                        str_tr +=
                            ' <td class="align-middle text-center">' +
                            self.result_reviews[i].kpi_score_6_month_ago +
                            "</td>";
                        // Kết quả (6 tháng trước)
                        str_tr +=
                            ' <td class="align-middle text-center">' +
                            self.result_reviews[i].result_6_month_ago +
                            "</td>";
                        // Kết quả (Hiện tại)
                        str_tr +=
                            ' <td class="align-middle text-center">' +
                            self.result_reviews[i].result_6_month +
                            "</td>";
                        // Ngày đánh giá
//                        str_tr +=
//                            ' <td class="align-middle text-left">' +
//                            self.result_reviews[i].ngay_danh_gia +
//                            "</td>";
                        str_tr += ' <td class="align-middle text-center">' +
                        formatDate(self.result_reviews[i].ngay_danh_gia) +
                        "</td>";

                        function formatDate(dateString) {
                            var dateParts = dateString.split('-');
                            if (dateParts.length === 3) {
                                var year = dateParts[0];
                                var month = dateParts[1];
                                var day = dateParts[2];
                                return day + '/' + month + '/' + year;
                            }
                            return dateString; // Trả về ngày gốc nếu không thể định dạng
                        }

                        // Xem thông tin chi tiết đánh giá
                        str_tr +=
                            '<td class="align-middle text-center"><button class="btn btn-primary btn-view-evaluation" data-evaluation-id="' +
                            self.result_reviews[i].id +
                            '">Xem Đánh giá</button></td>';
                    }
                    str_tr += "</tr>";

                    tbody_manage_reviews_all += str_tr;
                }
            }

            self.$("#tbody_manage_reviews_all").html(tbody_manage_reviews_all);
        },
    });

    core.action_registry.add("dashboard_manage_reviews", DashboardReviews);
    return DashboardReviews;
});
