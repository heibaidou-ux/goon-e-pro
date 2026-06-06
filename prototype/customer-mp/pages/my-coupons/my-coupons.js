const API = require('../../utils/api')
Page({ data: { coupons: [] }, onLoad() { API.getUserCoupons().then(coupons => this.setData({ coupons })) } })