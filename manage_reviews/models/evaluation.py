from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Evaluation(models.Model):
    _name = 'manage_reviews.evaluation'
    _description = 'Đánh giá'
    _rec_name = 'employee_id'

    # Tạo liên kết đến module hr - Lấy dữ liệu từ model hr.employee
    employee_id = fields.Many2one('hr.employee', string='Nhân sự', required=True)
    ten_nhansu = fields.Char(related='employee_id.name', string='Nhân sự được đánh giá')
    chuc_vu = fields.Char(related='employee_id.job_title', string='Chức vụ')
    quanly_tructiep = fields.Many2one(related='employee_id.parent_id', string='Manager')
    phong_ban = fields.Many2one(related='employee_id.department_id', string='Phòng ban', store=True)
    truong_phong_ban = fields.Many2one(related='employee_id.coach_id', string='Trưởng Phòng/Ban')
    image_1920 = fields.Image(related='employee_id.image_1920', string='Hình ảnh')

    # Lấy dữ liệu kỹ năng của nhân viên
    employee_skill_ids = fields.One2many(related='employee_id.employee_skill_ids', string="Skill Addvanced", readonly=True)
    skill_type_id = fields.Many2one(related='employee_id.employee_skill_ids.skill_type_id', string='Kỹ năng chính')
    skill_id = fields.Many2one(related='employee_id.employee_skill_ids.skill_id', string="Chi tiết Kỹ năng")
    skill_level_id = fields.Many2one(related='employee_id.employee_skill_ids.skill_level_id', string="Level")
    level_progress = fields.Integer(related='employee_id.employee_skill_ids.skill_level_id.level_progress', string='Cấp độ')

    ngay_danh_gia = fields.Date(string='Ngày đánh giá', default_type='date', required=True)

    # Tạo liên kết đến biểu mẫu
    evaluation_template_id = fields.Many2one('manage_reviews.template', string='Biểu mẫu', required=True)

    # Tạo liên kết đến điểm đánh giá
    score_ids = fields.One2many('manage_reviews.score', 'score_criteria_id', string='Điểm đánh giá')

    # Trạng thái đánh giá
    status = fields.Selection([
        ('chua_danh_gia', 'Chưa đánh giá'),
        ('da_danh_gia', 'Đã đánh giá'),
    ], string="Trạng thái", default='chua_danh_gia')

    # Lấy dữ liệu từ bảng điểm gồm: Tổng trọng số các tiêu chí và tổng điểm có trọng số (Cấp quản lý)
    realated_sum_score_manager = fields.Integer(related='score_ids.total_manager_weighted_score', string='Tổng Điểm có trọng số (Quản lý)')
    realated_sum_ts = fields.Integer(related='score_ids.total_trong_so_tc', string='Tổng trọng số')

    # Tính điểm KPI và đưa ra quyết định
    kpi_score = fields.Float(compute='_compute_kpi_score', string='Tổng điểm KPI', digits=(5, 2))
    result_6_month = fields.Char(string='Quyết định (6 tháng)', compute='_compute_result_6_month')

    kpi_score_history = fields.Float(string='Lịch sử Điểm KPI', compute='_compute_kpi_score_history')
    kpi_score_6_month_ago = fields.Float(string='Điểm KPI (6 tháng trước)', digits=(5, 2), compute='_compute_kpi_score_6_month_ago')
    result_6_month_ago = fields.Char(string='Quyết định (6 tháng trước)', compute='_compute_result_6_month_ago')

    # # Kiểm tra ngày đánh giá
    # @api.constrains('ngay_danh_gia')
    # def _check_ngay_danh_gia(self):
    #     for record in self:
    #         if record.ngay_danh_gia > date.today():
    #             raise models.ValidationError("Ngày đánh giá không được lớn hơn ngày hiện tại!")

    @api.depends('employee_id', 'ngay_danh_gia')
    def _compute_kpi_score_history(self):
        for record in self:
            evaluations = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('ngay_danh_gia', '<', record.ngay_danh_gia),
            ], order='ngay_danh_gia desc')

            if evaluations:
                record.kpi_score_history = evaluations[0].kpi_score
            else:
                record.kpi_score_history = 0.0

    @api.depends('kpi_score_history')
    def _compute_kpi_score_6_month_ago(self):
        for record in self:
            record.kpi_score_6_month_ago = record.kpi_score_history

    @api.depends('kpi_score_6_month_ago')
    def _compute_result_6_month_ago(self):
        for record in self:
            record.result_6_month_ago = record._get_result_6_month(record.kpi_score_6_month_ago)

    @api.depends('score_ids.total_manager_weighted_score', 'score_ids.total_trong_so_tc')
    def _compute_kpi_score(self):
        for record in self:
            if record.score_ids:
                total_manager_weighted_score = sum(score.manager_weighted_score for score in record.score_ids)
                total_trong_so_tc = sum(score.trong_so_tc for score in record.score_ids)

                if total_trong_so_tc != 0:
                    kpi_score = total_manager_weighted_score / total_trong_so_tc
                else:
                    kpi_score = 0.0
            else:
                kpi_score = 0.0

            record.kpi_score = kpi_score
            record.result_6_month = record._get_result_6_month(kpi_score)

    def _get_result_6_month(self, kpi_score):
        if kpi_score < 2.0:
            return "Yếu - Không tăng không giảm"
        elif 2.0 <= kpi_score <= 2.7:
            return "Trung bình - Tăng 5% lương"
        elif 2.8 <= kpi_score <= 3.1:
            return "Khá - Tăng 10% lương"
        elif 3.2 <= kpi_score <= 4.0:
            return "Tốt - Tăng 15% lương"

    @api.onchange("evaluation_template_id")
    def get_criteria_scores(self):
        if self.evaluation_template_id:
            self.score_ids = [(5, 0, 0)] + [(0, 0, {
                'name': line.name,
                'trong_so_tc': line.trong_so_tc,
                'mucdo_yeu': line.mucdo_yeu,
                'mucdo_trungbinh': line.mucdo_trungbinh,
                'mucdo_kha': line.mucdo_kha,
                'mucdo_tot': line.mucdo_tot,
                'employee_unweighted_score': 0,
                'employee_weighted_score': 0,
                'manager_unweighted_score': 0,
                'manager_weighted_score': 0,
            }) for line in self.evaluation_template_id.criteria_ids]


    @api.model
    def get_phong_ban(self):
        departments = self.env['manage_reviews.evaluation'].search([]).mapped('phong_ban.name')
        return departments

    @api.model
    def get_data_reviews(self, from_date, to_date, select_phong_ban=False):
        arr_search = []

        table_body = []
        result_status_chart = []
        result_score_chart = []

        yeu = 0
        trung_binh = 0
        kha = 0
        gioi = 0

        if select_phong_ban:
            arr_search.append(('phong_ban', '=', select_phong_ban))

        # Chuyển đổi từ chuỗi thành đối tượng ngày
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()

        for line in self.search(arr_search):
            ngay_danh_gia = line.ngay_danh_gia
            if from_date <= ngay_danh_gia <= to_date:
                kpi_score_6_month_ago = line.kpi_score_6_month_ago
                table_body.append({
                    'id': line.id,
                    'ten_nhansu': line.ten_nhansu,
                    'kpi_score': line.kpi_score,
                    'kpi_score_6_month_ago': kpi_score_6_month_ago,
                    'result_6_month': line.result_6_month,
                    'result_6_month_ago': line._get_result_6_month(kpi_score_6_month_ago),
                    'ngay_danh_gia': ngay_danh_gia
                })
                result_score_chart.append({
                    'ten_nhansu': line.ten_nhansu,
                    'kpi_score': line.kpi_score,
                })

        for item in table_body:
            kpi_score = item['kpi_score']
            if kpi_score < 2.0:
                yeu += 1
            elif 2.0 <= kpi_score <= 2.7:
                trung_binh += 1
            elif 2.8 <= kpi_score <= 3.1:
                kha += 1
            elif 3.2 <= kpi_score <= 4.0:
                gioi += 1

        result_status_chart.append({
            'yeu': yeu,
            'trung_binh': trung_binh,
            'kha': kha,
            'gioi': gioi
        })

        result = [result_status_chart, result_score_chart, table_body]
        return result


    @api.model
    def get_data_skill(self, select_phong_ban):
        skill_data = {}

        evaluations = self.env['manage_reviews.evaluation'].search([('phong_ban', '=', select_phong_ban)])

        for evaluation in evaluations:
            if evaluation.employee_skill_ids:
                for skill in evaluation.employee_skill_ids:
                    skill_name = skill.skill_id.name
                    if skill_name not in skill_data:
                        skill_data[skill_name] = {'employees': [], 'levels': {}, 'count': 0}
                    skill_data[skill_name]['employees'].append(evaluation.ten_nhansu)
                    skill_data[skill_name]['levels'][evaluation.ten_nhansu] = skill.skill_level_id.name
                    skill_data[skill_name]['count'] += 1

        result = skill_data
        print(result)  # Thêm log để kiểm tra giá trị result
        return result

