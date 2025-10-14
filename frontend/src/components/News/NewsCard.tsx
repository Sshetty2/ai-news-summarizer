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
      className="news-card hover:shadow-lg transition-all duration-200 cursor-pointer"
      onClick={handleCardClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <CardTitle className="text-lg leading-tight line-clamp-3">
            {article.title}
          </CardTitle>
          {article.url_to_image && (
            <img
              src={article.url_to_image}
              alt={article.title}
              className="w-16 h-16 object-cover rounded-md flex-shrink-0"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          )}
        </div>
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="font-medium text-primary">{article.source_name}</span>
          {article.author && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1">
                <User className="h-3 w-3" />
                <span>{article.author}</span>
              </div>
            </>
          )}
          <span>•</span>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>{article.published_at}</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {article.description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
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

          <div className="flex items-center gap-1">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={handleExternalClick}
              className="h-8 px-2"
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
            
            {showAnalysisButton && (
              <Button
                variant={article.has_analysis ? "secondary" : "default"}
                size="sm"
                onClick={handleAnalyzeClick}
                disabled={isAnalyzing}
                className="h-8 px-3"
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
                      {article.has_analysis ? 'View Analysis' : 'Analyze'}
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
