export const isExternal = (path: string) => /^(https?:|mailto:|tel:)/.test(path)

export const isValidPassword = (str: string) => /^[\w]{6,18}$/.test(str)
