const API = require('../../utils/staff-api')
Page({ data: { todos: [] }, onShow() { API.getTodos().then(todos => this.setData({ todos })) } })
