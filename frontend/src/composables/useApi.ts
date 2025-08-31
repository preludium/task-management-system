import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const useApi = () => {
  async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await client.get(url, config)
    return response.data
  }

  async function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await client.post(url, data, config)
    return response.data
  }

  async function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await client.put(url, data, config)
    return response.data
  }

  async function deleteRequest<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await client.delete(url, config)
    return response.data
  }

  return {
    get,
    post,
    put,
    delete: deleteRequest,
  }
}