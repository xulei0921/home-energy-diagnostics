// 生成随机RGB颜色
export const getRandomRgbaColor = (opacity = 0.7) => {
    const r = Math.floor(Math.random() * 256)
    const g = Math.floor(Math.random() * 256)
    const b = Math.floor(Math.random() * 256)
    return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

// 生成一组随机颜色对
export const generateRandomColorPairs = (count) => {
    return Array.from({ length: count }, () => ({
        borderColor: 'rgb(255, 255, 255)',
        backgroundColor: getRandomRgbaColor(0.7)
    }))
}