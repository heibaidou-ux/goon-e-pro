const API = require('../../utils/api')
Page({ data: { todos: [] }, onShow() { API.getTodos().then(todos => this.setData({ todos })) } })