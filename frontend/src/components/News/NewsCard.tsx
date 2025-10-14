import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { type NewsArticle } from '@/lib/api'
import { 
  ExternalLink, 
  BarChart3, 
  Clock, 
  User
} from 'lucide-react'

interface NewsCardProps {
  article: NewsArticle
  onAnalyze?: (article: NewsArticle) => void
  onRead?: (article: NewsArticle) => void
  isAnalyzing?: boolean
  showAnalysisButton?: boolean
}

const NewsCard: React.FC<NewsCardProps> = ({
  article,
  onAnalyze,
  onRead,
  isAnalyzing = false,
  showAnalysisButton = true
}) => {
  const handleAnalyzeClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onAnalyze?.(article)
  }

  const handleCardClick = () => {
    onRead?.(article)
  }

  const handleExternalClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    window.open(article.url, '_blank', 'noopener,noreferrer')
  }

  return (
    <Card
      className="news-card hover:shadow-lg transition-all duration-200 cursor-pointer h-full flex flex-col"
      onClick={handleCardClick}
    >
      {article.url_to_image && (
        <div className="w-full h-48 overflow-hidden">
          <img
            src={article.url_to_image}
            alt={article.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.parentElement!.style.display = 'none'
            }}
          />
        </div>
      )}

      <CardHeader className="pb-3 flex-none">
        <CardTitle className="text-base leading-tight line-clamp-2">
          {article.title}
        </CardTitle>

        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
          <span className="font-medium text-primary truncate">{article.source_name}</span>
          <span>•</span>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3 flex-shrink-0" />
            <span className="truncate">{article.published_at}</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 flex-1 flex flex-col justify-between">
        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
          {article.description}
        </p>

        <div className="space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            {article.category_name && (
              <Badge variant="secondary" className="text-xs">
                {article.category_name}
              </Badge>
            )}
            {article.has_analysis && (
              <Badge variant="outline" className="text-xs">
                <BarChart3 className="h-3 w-3 mr-1" />
                Analyzed
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2 justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExternalClick}
              className="h-7 px-2 flex-shrink-0"
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              <span className="text-xs">Read</span>
            </Button>

            {showAnalysisButton && (
              <Button
                variant={article.has_analysis ? "secondary" : "default"}
                size="sm"
                onClick={handleAnalyzeClick}
                disabled={isAnalyzing}
                className="h-7 px-3 flex-1"
              >
                {isAnalyzing ? (
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    <span className="text-xs">Analyzing...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1">
                    <BarChart3 className="h-3 w-3" />
                    <span className="text-xs">
                      {article.has_analysis ? 'View' : 'Analyze'}
                    </span>
                  </div>
                )}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default NewsCard
