class VoucherStatusOut(BaseModel):
    has_active_voucher: bool
    is_vip_plus: bool
    expires_at: str | None
    product_quota_used: int
    product_quota_total: int
    paid_quota_used: int
    paid_quota_total: int
