/**
 * 高岸荟 小程序上传脚本
 *
 * 用法:
 *   上传:   node upload.js customer-mp
 *   预览:   node upload.js customer-mp --preview
 *   上传:   node upload.js staff-mp
 *
 * 前置条件:
 *   1. npm install
 *   2. 将微信公众平台下载的 private.key 放到本项目根目录
 *   3. 版本号在命令行指定，如: node upload.js customer-mp --version 1.0.0
 */
const path = require('path')
const ci = require('miniprogram-ci')
const fs = require('fs')

const projectRoot = __dirname
const privateKeyPath = path.join(projectRoot, 'private.key')

// 小程序配置
const PROJECTS = {
  'customer-mp': {
    name: '高岸荟',
    appid: 'wx181568857908b5ae',
    projectPath: path.join(projectRoot, 'customer-mp'),
    desc: '客人端 - 预约/商城/扫码消费',
  },
  'staff-mp': {
    name: '高岸ERP店员端',
    appid: 'wx181568857908b5ae',
    projectPath: path.join(projectRoot, 'staff-mp'),
    desc: '店员端 - 房态/设备/保洁/订单',
  }
}

async function main() {
  const projectName = process.argv[2]
  const isPreview = process.argv.includes('--preview')
  const version = process.argv.find(a => a.startsWith('--version='))?.split('=')[1] || '1.0.0'

  if (!projectName || !PROJECTS[projectName]) {
    console.error('用法: node upload.js [customer-mp|staff-mp] [--preview] [--version=1.0.0]')
    console.error('可用项目:')
    Object.keys(PROJECTS).forEach(k => console.error(`  ${k} - ${PROJECTS[k].desc}`))
    process.exit(1)
  }

  if (!fs.existsSync(privateKeyPath)) {
    console.error(`
❌ 未找到私钥文件: ${privateKeyPath}

请在微信公众平台下载上传密钥:
  1. 登录 https://mp.weixin.qq.com
  2. 开发管理 → 开发设置 → 小程序代码 → 上传密钥
  3. 生成并下载 private.key
  4. 放到 prototype/ 目录下
`)
    process.exit(1)
  }

  const config = PROJECTS[projectName]

  const project = new ci.Project({
    appid: config.appid,
    type: 'miniProgram',
    projectPath: config.projectPath,
    privateKeyPath,
    ignores: ['node_modules/**/*'],
  })

  try {
    if (isPreview) {
      console.log(`\n📱 生成预览二维码: ${config.name} v${version}`)
      const result = await ci.preview({
        project,
        desc: config.desc,
        setting: { es6: true, es7: true, minify: true },
        qrcodeFormat: 'image',
        qrcodeOutputDest: path.join(projectRoot, `preview-${projectName}.jpg`),
      })
      console.log(`✅ 预览二维码已生成: preview-${projectName}.jpg`)
    } else {
      console.log(`\n📦 上传: ${config.name} v${version}`)
      console.log(`   描述: ${config.desc}`)

      const result = await ci.upload({
        project,
        version,
        desc: config.desc,
        setting: { es6: true, es7: true, minify: true },
        onProgressUpdate: console.log,
      })

      console.log(`\n✅ 上传成功! 版本: ${version}`)
      console.log(`   前往 https://mp.weixin.qq.com 提交审核`)
    }
  } catch (err) {
    console.error('\n❌ 上传失败:', err.message || err)
    process.exit(1)
  }
}

main()
