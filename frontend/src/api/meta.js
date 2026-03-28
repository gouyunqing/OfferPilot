import { get } from '@/utils/request'

export const getCompanies = () => get('/v1/meta/companies', null, { loading: false })
export const getPositions = () => get('/v1/meta/positions', null, { loading: false })
export const getRounds = () => get('/v1/meta/rounds', null, { loading: false })
export const getCompanyStats = () => get('/v1/meta/companies/stats', null, { loading: false })
