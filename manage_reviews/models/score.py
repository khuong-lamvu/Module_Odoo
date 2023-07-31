from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EvaluationScore(models.Model):
    _name = 'manage_reviews.score'
    _description = 'Điểm đánh giá'

    score_criteria_id = fields.Many2one('manage_reviews.evaluation', string='Đánh giá điểm')
    mucdo_yeu = fields.Char(string='Yếu (1)', readonly=True, store=True)
    mucdo_trungbinh = fields.Char(string='Trung Bình (2)', readonly=True, store=True)
    mucdo_kha = fields.Char(string='Khá (3)', readonly=True, store=True)
    mucdo_tot = fields.Char(string='Tốt (4)', readonly=True, store=True)


    name = fields.Char(string='Tiêu chí', readonly=True, store=True)

    trong_so_tc = fields.Integer(string='Trọng số', readonly=True, store=True)
    total_trong_so_tc = fields.Integer(
        string='Tổng Trọng số',
        compute='_compute_total_trong_so_tc',
        store=True
    )

    employee_unweighted_score = fields.Integer(string='Điểm chưa có trọng số (Nhân viên)')
    employee_weighted_score = fields.Integer(string='Điểm có trọng số (Nhân viên)', readonly=True, store=True)
    manager_unweighted_score = fields.Integer(string='Điểm chưa có trọng số (Quản lý)')
    manager_weighted_score = fields.Integer(string='Điểm có trọng số (Quản lý)', readonly=True, store=True)

    total_manager_weighted_score = fields.Integer(
        string='Tổng Điểm có trọng số (Quản lý)',
        compute='_compute_total_manager_weighted_score',
        store=True
    )
    # Tính tổng Điểm (có trọng số) = Điểm chưa có trọng số x Trọng số
    # Tính điểm có trọng số (Cấp nhân viên)
    @api.depends('trong_so_tc')
    def _compute_total_trong_so_tc(self):
        for record in self:
            record.total_trong_so_tc = sum(record.trong_so_tc for record in self)

    # Tính điểm có trọng số (Cấp quản lý)
    @api.onchange('employee_unweighted_score', 'trong_so_tc')
    def _onchange_employee_unweighted_score(self):
        if self.trong_so_tc:
            self.employee_weighted_score = int(self.employee_unweighted_score * float(self.trong_so_tc))
        else:
            self.employee_weighted_score = 0

    # Tính tổng của Điểm khi có trọng số (Nhân viên)
    @api.onchange('manager_unweighted_score', 'trong_so_tc')
    def _onchange_manager_unweighted_score(self):
        if self.trong_so_tc:
            self.manager_weighted_score = int(self.manager_unweighted_score * float(self.trong_so_tc))
        else:
            self.manager_weighted_score = 0

    # Tính tổng của Điểm khi có trọng số (Quản lý)
    @api.depends('manager_weighted_score')
    def _compute_total_manager_weighted_score(self):
        for record in self:
            record.total_manager_weighted_score = sum(record.manager_weighted_score for record in self)