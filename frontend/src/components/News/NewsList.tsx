import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import NewsCard from './NewsCard'
import { type NewsArticle, type NewsCategory } from '@/lib/api'
import { 
  Filter,
  Search,
  RefreshCw,
  Loader2,
  AlertCircle,
  Download
} from 'lucide-react'

interface NewsListProps {
  articles: NewsArticle[]
  categories: NewsCategory[]
  onAnalyzeArticle?: (article: NewsArticle) => void
  onRefresh?: () => void
  onSearch?: (query: string) => void
  onCategoryFilter?: (category: string | null) => void
  onFetchNews?: () => void
  isLoading?: boolean
  isFetching?: boolean
  error?: string
  selectedCategory?: string | null
  analyzingArticleId?: number | null
}

const NewsList: React.FC<NewsListProps> = ({
  articles,
  categories,
  onAnalyzeArticle,
  onRefresh,
  onSearch,
  onCategoryFilter,
  onFetchNews,
  isLoading = false,
  isFetching = false,
  error,
  selectedCategory,
  analyzingArticleId
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    onSearch?.(query)
  }

  const handleCategoryClick = (categorySlug: string | null) => {
    onCategoryFilter?.(categorySlug)
  }

  return (
    <div className="space-y-4 px-2">
      {/* Search and Filter Controls */}
      <div className="space-y-3">
        <div className="flex gap-2 items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-9 h-10"
            />
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowFilters(!showFilters)}
            className="h-10 w-10"
          >
            <Filter className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={onRefresh}
            disabled={isLoading}
            className="h-10 w-10"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Category Filters */}
        {showFilters && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Filter by Category</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex flex-wrap gap-2">
                <Badge
                  variant={selectedCategory === null ? "default" : "secondary"}
                  className="cursor-pointer"
                  onClick={() => handleCategoryClick(null)}
                >
                  All Categories
                </Badge>
                {categories.map((category) => (
                  <Badge
                    key={category.slug}
                    variant={selectedCategory === category.slug ? "default" : "secondary"}
                    className="cursor-pointer"
                    onClick={() => handleCategoryClick(category.slug)}
                  >
                    {category.name} ({category.article_count})
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {isLoading && articles.length === 0 && (
        <div className="flex justify-center py-12">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading articles...</span>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && articles.length === 0 && !error && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No articles found</h3>
              <p className="text-sm mb-4">
                {searchQuery 
                  ? `No articles found for "${searchQuery}"`
                  : selectedCategory
                  ? `No articles found in the ${selectedCategory} category`
                  : 'No articles available. Fetch the latest news to get started!'
                }
              </p>
              <div className="flex gap-2 justify-center">
                {(searchQuery || selectedCategory) && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSearchQuery('')
                      handleSearch('')
                      handleCategoryClick(null)
                    }}
                  >
                    Clear Filters
                  </Button>
                )}
                {!searchQuery && !selectedCategory && onFetchNews && (
                  <Button
                    onClick={onFetchNews}
                    disabled={isFetching}
                  >
                    {isFetching ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Fetching News...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Fetch Latest News
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Articles Grid - 3 columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {articles.map((article) => (
          <NewsCard
            key={article.id}
            article={article}
            onAnalyze={onAnalyzeArticle}
            isAnalyzing={analyzingArticleId === article.id}
            showAnalysisButton={true}
          />
        ))}
      </div>

      {/* Load More Button (if needed) */}
      {articles.length > 0 && !isLoading && (
        <div className="text-center py-4">
          <Button variant="outline">
            Load More Articles
          </Button>
        </div>
      )}
    </div>
  )
}

export default NewsList
