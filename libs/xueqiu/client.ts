/**
 * 雪球 HTTP 客户端
 *
 * 功能：封装雪球API的HTTP请求
 * 依赖：需要雪球Cookie才能访问
 *
 * 使用方法：
 * 1. 登录雪球网页版
 * 2. 复制请求头中的 Cookie
 * 3. 设置环境变量或配置文件
 */

interface XueqiuConfig {
  baseUrl: string
  stockUrl: string
  cookie?: string
  timeout: number
}

interface XueqiuRequestOptions {
  path: string
  method?: 'GET' | 'POST'
  params?: Record<string, string | number | boolean>
  headers?: Record<string, string>
  useStockUrl?: boolean
}

interface XueqiuResponse<T = unknown> {
  error_code: number
  error_description?: string
  data?: T
}

class XueqiuClient {
  private config: XueqiuConfig
  private cookie: string = ''
  private initialized: boolean = false

  private static readonly DEFAULT_HEADERS: Record<string, string> = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://xueqiu.com/',
    'Origin': 'https://xueqiu.com',
  }

  constructor(config: Partial<XueqiuConfig> = {}) {
    this.config = {
      baseUrl: 'https://xueqiu.com',
      stockUrl: 'https://stock.xueqiu.com',
      timeout: 30000,
      ...config,
    }
  }

  /**
   * 初始化会话，访问首页获取必要的cookie
   */
  async initialize(): Promise<void> {
    if (this.initialized) return

    try {
      await this.request({
        path: '/',
        method: 'GET',
        useStockUrl: false,
      })
      this.initialized = true
    } catch (error) {
      console.warn('雪球客户端初始化失败（这可能不影响功能）:', error)
      this.initialized = true
    }
  }

  /**
   * 设置认证Cookie
   */
  setCookie(cookie: string): void {
    this.cookie = cookie
  }

  /**
   * 构建URL
   */
  private buildUrl(options: XueqiuRequestOptions): string {
    const baseUrl = options.useStockUrl ? this.config.stockUrl : this.config.baseUrl
    return `${baseUrl}${options.path}`
  }

  /**
   * 构建查询参数
   */
  private buildQueryString(params?: Record<string, string | number | boolean>): string {
    if (!params) return ''

    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    }
    return searchParams.toString()
  }

  /**
   * 发起请求
   */
  async request<T = unknown>(options: XueqiuRequestOptions): Promise<T> {
    const { method = 'GET', params, headers } = options

    const url = this.buildUrl(options)
    const queryString = this.buildQueryString(params)
    const finalUrl = queryString ? `${url}?${queryString}` : url

    const requestHeaders: Record<string, string> = {
      ...XueqiuClient.DEFAULT_HEADERS,
      ...headers,
    }

    if (this.cookie) {
      requestHeaders['Cookie'] = this.cookie
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout)

    try {
      const response = await fetch(finalUrl, {
        method,
        headers: requestHeaders,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new XueqiuError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
        )
      }

      const text = await response.text()

      try {
        const data: XueqiuResponse<T> = JSON.parse(text)

        if (data.error_code !== 0) {
          throw new XueqiuError(
            data.error_description || `API错误: ${data.error_code}`,
            data.error_code,
            data,
          )
        }

        return data.data as T
      } catch (parseError) {
        if (parseError instanceof XueqiuError) throw parseError
        throw new XueqiuError(`响应解析失败: ${parseError}`, -1, text)
      }
    } catch (error) {
      clearTimeout(timeoutId)

      if (error instanceof XueqiuError) {
        throw error
      }

      if (error instanceof Error && error.name === 'AbortError') {
        throw new XueqiuError(`请求超时 (${this.config.timeout}ms)`, -2)
      }

      throw new XueqiuError(`网络请求失败: ${error}`, -3)
    }
  }

  /**
   * 获取股票实时报价
   */
  async getQuote(symbol: string): Promise<Record<string, unknown>> {
    await this.initialize()
    return this.request({
      path: '/v5/stock/quote.json',
      params: { symbol, extend: 'detail' },
      useStockUrl: true,
    })
  }

  /**
   * 获取K线数据
   */
  async getKline(
    symbol: string,
    options: {
      period?: string
      count?: number
      begin?: number
    } = {},
  ): Promise<{ column: string[]; item: unknown[][] }> {
    await this.initialize()
    const { period = 'day', count = 100, begin = Math.floor(Date.now() / 1000) } = options

    return this.request({
      path: '/v5/stock/chart/kline.json',
      params: {
        symbol,
        begin,
        period,
        type: 'before',
        count: -count,
        indicator: 'kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance',
      },
      useStockUrl: true,
    })
  }

  /**
   * 获取热门股票
   */
  async getHotStocks(options: {
    market?: 'CN' | 'HK' | 'US'
    count?: number
  } = {}): Promise<unknown[]> {
    await this.initialize()
    const { market = 'CN', count = 10 } = options

    return this.request({
      path: '/v5/stock/hot_stock/list.json',
      params: {
        size: count,
        type: market,
        _type: '10',
      },
      useStockUrl: true,
    })
  }

  /**
   * 获取市场状态
   */
  async getMarketStatus(): Promise<Record<string, unknown>> {
    await this.initialize()
    return this.request({
      path: '/v5/stock/batch/quote.json',
      params: {
        symbol: 'SH000001,SZ399001,SZ399006',
      },
      useStockUrl: true,
    })
  }

  /**
   * 搜索股票
   */
  async search(query: string, count: number = 10): Promise<unknown[]> {
    await this.initialize()
    return this.request({
      path: '/v5/stock/search.json',
      params: { q: query, size: count },
      useStockUrl: true,
    })
  }

  /**
   * 获取用户持仓
   */
  async getPortfolio(): Promise<unknown> {
    await this.initialize()
    return this.request({
      path: '/v5/user/portfolio/stock.json',
      useStockUrl: false,
    })
  }

  /**
   * 获取自选股列表
   */
  async getWatchlist(): Promise<unknown> {
    await this.initialize()
    return this.request({
      path: '/v5/user/stock/snapshot.json',
      useStockUrl: false,
    })
  }
}

class XueqiuError extends Error {
  code: number
  response?: unknown

  constructor(message: string, code: number, response?: unknown) {
    super(message)
    this.name = 'XueqiuError'
    this.code = code
    this.response = response
  }
}

export { XueqiuClient, XueqiuError }
export type { XueqiuConfig, XueqiuRequestOptions, XueqiuResponse }
