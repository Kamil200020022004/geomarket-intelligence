
import { useCallback, useEffect, useState } from "react"

import {
  getFavorites,
  addFavorite,
  removeFavorite,
  getFavoriteId,
  subscribeToFavorites,
} from "../services/favoritesService"

export default function useFavorites(type, userId) {
  const [favorites, setFavorites] = useState([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (userId === null || userId === undefined) {
      setFavorites([])
      setError("")
      return
    }

    setLoading(true)

    try {
      const items = await getFavorites(userId, type)
      setFavorites(items)
      setError("")
    } catch (err) {
      setFavorites([])
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [type, userId])

  useEffect(() => {
    let active = true

    setFavorites([])
    setError("")

    async function load() {
      if (userId === null || userId === undefined) {
        return
      }

      try {
        const items = await getFavorites(userId, type)

        if (active) {
          setFavorites(items)
          setError("")
        }
      } catch (err) {
        if (active) {
          setError(err.message)
        }
      }
    }

    load()

    const unsubscribe = subscribeToFavorites((detail) => {
      if (
        !detail ||
        (detail.userId === String(userId) && detail.type === type)
      ) {
        load()
      }
    })

    return () => {
      active = false
      unsubscribe()
    }
  }, [type, userId])

  const isFavorite = useCallback(
    (id) =>
      favorites.some(
        (item) => getFavoriteId(item) === String(id)
      ),
    [favorites]
  )

  const toggleFavorite = useCallback(
    async (item) => {
      if (userId === null || userId === undefined) {
        throw new Error("Zaloguj się, aby zapisać ulubione.")
      }

      const id = getFavoriteId(item)

      if (!id) {
        throw new Error("Brak identyfikatora elementu.")
      }

      setLoading(true)

      try {
        const updated = isFavorite(id)
          ? await removeFavorite(userId, type, id)
          : await addFavorite(userId, type, item)

        setFavorites(updated)
        setError("")

        return updated
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [type, userId, isFavorite]
  )

  return {
    favorites,
    loading,
    error,
    isFavorite,
    toggleFavorite,
    refresh,
  }
}
