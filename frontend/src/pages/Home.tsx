import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Chip,
  Container,
  Skeleton,
  Paper,
  Stack,
  Fade,
  Grow,
  Zoom,
  Fab,
  Tooltip,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Science,
  People,
  School,
  ArrowForward,
  KeyboardArrowDown,
  PlayArrow,
  Business,
  LocalPharmacy,
} from '@mui/icons-material';
import axios from 'axios';

interface Comment {
  id: number;
  content: string;
  author: {
    id: number;
    name: string;
    profile_picture_url?: string;
  };
  post: {
    id: number;
    title: string;
  };
  created_at: string;
}

const Home: React.FC = () => {
  const [recentComments, setRecentComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await axios.get('/api/pages/home');
        setRecentComments(response.data.recent_comments);
      } catch (error) {
        console.error('Error fetching home data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  const scrollToVision = () => {
    document.getElementById('vision')?.scrollIntoView({ behavior: 'smooth' });
  };

  const goals = [
    {
      icon: Science,
      title: 'Advance Research',
      description: 'To promote and facilitate high-quality research in pharmaceutical sciences, encouraging students to explore innovative solutions to real-world health challenges.',
      color: 'primary.main',
    },
    {
      icon: People,
      title: 'Foster Collaboration',
      description: 'To build partnerships between students, faculty, and industry experts, creating a collaborative environment that enhances learning and professional development.',
      color: 'secondary.main',
    },
    {
      icon: School,
      title: 'Educate and Inspire',
      description: 'To educate the community about pharmaceutical sciences and inspire the next generation of researchers and healthcare professionals.',
      color: 'primary.light',
    },
  ];

  const partners = [
    { name: 'Faculty of Pharmacy, UofK', logo: '/static/images/uofk.jpg' },
    { name: 'FPSA', logo: '/static/images/fpsa.jpg' },
    { name: 'PharmaRx', logo: '/static/images/PharmaRx.png' },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          backgroundImage: 'url(/static/images/image1.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(45, 87, 123, 0.9), rgba(96, 125, 155, 0.75))',
            backdropFilter: 'blur(1px)',
          },
          '&::after': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 40%, rgba(245, 158, 11, 0.1) 0%, transparent 50%), radial-gradient(circle at 70% 60%, rgba(45, 87, 123, 0.1) 0%, transparent 50%)',
          },
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Fade in={true} timeout={1000}>
            <Box textAlign="center" color="white">
              <Grow in={true} timeout={1500}>
                <Typography
                  variant="h1"
                  component="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', md: '4rem' },
                    fontWeight: 'bold',
                    mb: 3,
                    textShadow: '3px 3px 6px rgba(0,0,0,0.7), 0 0 20px rgba(245, 158, 11, 0.3)',
                    background: 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Pioneering Pharmaceutical Research
                </Typography>
              </Grow>

              <Zoom in={true} timeout={2000}>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 5,
                    maxWidth: '900px',
                    mx: 'auto',
                    textShadow: '2px 2px 4px rgba(0,0,0,0.6)',
                    lineHeight: 1.7,
                    fontSize: { xs: '1.1rem', md: '1.4rem' },
                  }}
                >
                  Join a community of innovators dedicated to advancing healthcare. Discover opportunities, collaborate on cutting-edge projects, and make an impact.
                </Typography>
              </Zoom>

              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={3}
                justifyContent="center"
                alignItems="center"
                sx={{ mt: 4 }}
              >
                <Tooltip title="Join our community today!" arrow placement="top">
                  <Button
                    variant="contained"
                    color="secondary"
                    size="large"
                    component={Link}
                    to="/register"
                    sx={{
                      px: 5,
                      py: 2.5,
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      borderRadius: 3,
                      boxShadow: '0 8px 25px rgba(245, 158, 11, 0.4)',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'translateY(-3px)',
                        boxShadow: '0 12px 35px rgba(245, 158, 11, 0.6)',
                      },
                    }}
                    startIcon={<LocalPharmacy />}
                  >
                    Join Now
                  </Button>
                </Tooltip>

                <Tooltip title="Learn more about our mission" arrow placement="top">
                  <Button
                    variant="outlined"
                    color="inherit"
                    size="large"
                    onClick={scrollToVision}
                    sx={{
                      px: 5,
                      py: 2.5,
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      borderRadius: 3,
                      borderWidth: 2,
                      borderColor: 'white',
                      color: 'white',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        borderColor: 'white',
                        bgcolor: 'rgba(255,255,255,0.15)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(255,255,255,0.2)',
                      },
                    }}
                    endIcon={<KeyboardArrowDown />}
                  >
                    Learn More
                  </Button>
                </Tooltip>
              </Stack>
            </Box>
          </Fade>
        </Container>

        {/* Floating Action Button */}
        <Zoom in={true} timeout={3000}>
          <Tooltip title="Quick Access" placement="left">
            <Fab
              color="secondary"
              size="large"
              sx={{
                position: 'absolute',
                bottom: 40,
                right: 40,
                boxShadow: '0 8px 25px rgba(245, 158, 11, 0.4)',
                '&:hover': {
                  transform: 'scale(1.1)',
                  boxShadow: '0 12px 35px rgba(245, 158, 11, 0.6)',
                },
                display: { xs: 'none', md: 'flex' },
              }}
              onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
            >
              <PlayArrow />
            </Fab>
          </Tooltip>
        </Zoom>
      </Box>

      {/* Vision Section */}
      <Box id="vision" sx={{ py: 8, bgcolor: 'background.paper' }}>
        <Container maxWidth="md">
          <Box textAlign="center">
            <Typography
              variant="h2"
              component="h2"
              color="primary"
              sx={{ mb: 4, fontWeight: 'bold' }}
            >
              Our Vision
            </Typography>
            <Typography
              variant="body1"
              sx={{ lineHeight: 1.8, fontSize: '1.1rem' }}
            >
              The Pharmaceutical Studies and Research Association (PSRA) is a student-led organization dedicated to fostering a culture of scientific inquiry and innovation in pharmaceutical sciences. We aim to bridge the gap between academic learning and real-world application by providing students with opportunities to engage in cutting-edge research, collaborate with industry professionals, and contribute to advancements in healthcare.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Goals Section */}
      <Box sx={{ py: 10, bgcolor: 'grey.50', position: 'relative', overflow: 'hidden' }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={8}>
            <Fade in={true} timeout={1000}>
              <Typography
                variant="h2"
                component="h2"
                color="primary"
                sx={{
                  mb: 3,
                  fontWeight: 'bold',
                  position: 'relative',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    bottom: -10,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 80,
                    height: 4,
                    bgcolor: 'secondary.main',
                    borderRadius: 2,
                  },
                }}
              >
                Our Goals
              </Typography>
            </Fade>
            <Fade in={true} timeout={1500}>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{
                  maxWidth: '600px',
                  mx: 'auto',
                  lineHeight: 1.6,
                }}
              >
                Driving innovation and excellence in pharmaceutical research through collaboration and education
              </Typography>
            </Fade>
          </Box>

          <Grid container spacing={4}>
            {goals.map((goal, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Grow in={true} timeout={1000 + index * 300}>
                  <Card
                    elevation={2}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      borderRadius: 3,
                      overflow: 'hidden',
                      position: 'relative',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                      '&:hover': {
                        transform: 'translateY(-12px) scale(1.02)',
                        boxShadow: (theme: any) => `0 20px 40px ${theme.palette.primary.main}20`,
                        '& .goal-icon-bg': {
                          transform: 'scale(1.1)',
                        },
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 4,
                        bgcolor: goal.color,
                      },
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 5 }}>
                      <Box
                        className="goal-icon-bg"
                        sx={{
                          width: 100,
                          height: 100,
                          borderRadius: '50%',
                          bgcolor: `${goal.color}15`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 4,
                          transition: 'transform 0.3s ease',
                        }}
                      >
                        <goal.icon
                          sx={{
                            fontSize: 48,
                            color: goal.color,
                            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
                          }}
                        />
                      </Box>

                      <Typography
                        variant="h5"
                        component="h3"
                        sx={{
                          mb: 3,
                          fontWeight: 'bold',
                          color: 'primary.main',
                        }}
                      >
                        {goal.title}
                      </Typography>

                      <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{
                          lineHeight: 1.7,
                          fontSize: '1rem',
                        }}
                      >
                        {goal.description}
                      </Typography>
                    </CardContent>

                    <Box
                      sx={{
                        p: 3,
                        pt: 0,
                        display: 'flex',
                        justifyContent: 'center',
                      }}
                    >
                      <Chip
                        label="Learn More"
                        variant="outlined"
                        color="primary"
                        size="small"
                        sx={{
                          borderRadius: 2,
                          fontWeight: 'medium',
                          '&:hover': {
                            bgcolor: 'primary.main',
                            color: 'white',
                          },
                        }}
                      />
                    </Box>
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Container>

        {/* Background decorative elements */}
        <Box
          sx={{
            position: 'absolute',
            top: '20%',
            right: '5%',
            width: 200,
            height: 200,
            borderRadius: '50%',
            bgcolor: 'primary.main',
            opacity: 0.03,
            zIndex: 0,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: '20%',
            left: '5%',
            width: 150,
            height: 150,
            borderRadius: '50%',
            bgcolor: 'secondary.main',
            opacity: 0.04,
            zIndex: 0,
          }}
        />
      </Box>

      {/* Recent Forum Discussions */}
      <Box sx={{ py: 10, bgcolor: 'background.paper', position: 'relative' }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={8}>
            <Fade in={true} timeout={1000}>
              <Typography
                variant="h2"
                component="h2"
                color="primary"
                sx={{
                  mb: 3,
                  fontWeight: 'bold',
                  position: 'relative',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    bottom: -10,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 80,
                    height: 4,
                    bgcolor: 'secondary.main',
                    borderRadius: 2,
                  },
                }}
              >
                Recent Forum Discussions
              </Typography>
            </Fade>
            <Fade in={true} timeout={1500}>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{
                  maxWidth: '700px',
                  mx: 'auto',
                  lineHeight: 1.6,
                }}
              >
                Join the conversation and connect with fellow researchers in our vibrant community
              </Typography>
            </Fade>
          </Box>

          {loading ? (
            <Grid container spacing={4}>
              {[...Array(3)].map((_, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card elevation={1} sx={{ borderRadius: 3, overflow: 'hidden' }}>
                    <CardContent sx={{ p: 4 }}>
                      <Box display="flex" alignItems="center" mb={3}>
                        <Skeleton variant="circular" width={50} height={50} sx={{ mr: 2 }} />
                        <Box sx={{ flex: 1 }}>
                          <Skeleton width="60%" height={24} sx={{ mb: 1 }} />
                          <Skeleton width="40%" height={16} />
                        </Box>
                      </Box>
                      <Skeleton height={80} sx={{ mb: 3, borderRadius: 2 }} />
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Skeleton width={120} height={32} sx={{ borderRadius: 16 }} />
                        <Skeleton width={100} height={36} sx={{ borderRadius: 2 }} />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : recentComments.length > 0 ? (
            <>
              <Grid container spacing={4} mb={6}>
                {recentComments.map((comment, index) => (
                  <Grid item xs={12} md={4} key={comment.id}>
                    <Grow in={true} timeout={1000 + index * 200}>
                      <Card
                        elevation={2}
                        sx={{
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          borderRadius: 3,
                          overflow: 'hidden',
                          position: 'relative',
                          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                          cursor: 'pointer',
                          '&:hover': {
                            transform: 'translateY(-8px) scale(1.01)',
                            boxShadow: (theme: any) => `0 16px 40px ${theme.palette.primary.main}15`,
                          },
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            height: 3,
                            bgcolor: 'secondary.main',
                          },
                        }}
                      >
                        <CardContent sx={{ flexGrow: 1, p: 4 }}>
                          <Box display="flex" alignItems="center" mb={3}>
                            <Tooltip title={comment.author.name} arrow>
                              <Avatar
                                src={comment.author.profile_picture_url || '/static/images/default-avatar.png'}
                                sx={{
                                  width: 50,
                                  height: 50,
                                  mr: 2,
                                  border: '2px solid',
                                  borderColor: 'primary.light',
                                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                }}
                              />
                            </Tooltip>
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="subtitle1"
                                fontWeight="bold"
                                color="primary.main"
                                sx={{ mb: 0.5 }}
                              >
                                {comment.author.name}
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                              >
                                <Business sx={{ fontSize: 14 }} />
                                {new Date(comment.created_at).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric'
                                })}
                              </Typography>
                            </Box>
                          </Box>

                          <Typography
                            variant="body2"
                            sx={{
                              mb: 3,
                              lineHeight: 1.7,
                              color: 'text.primary',
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {comment.content.length > 150
                              ? `${comment.content.substring(0, 150)}...`
                              : comment.content
                            }
                          </Typography>

                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Tooltip title={`Discussion: ${comment.post.title}`} arrow>
                              <Chip
                                label={comment.post.title.length > 20
                                  ? `${comment.post.title.substring(0, 20)}...`
                                  : comment.post.title
                                }
                                size="small"
                                color="primary"
                                variant="outlined"
                                sx={{
                                  borderRadius: 2,
                                  fontWeight: 'medium',
                                  '&:hover': {
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                  },
                                }}
                              />
                            </Tooltip>

                            <Tooltip title="Continue reading" arrow>
                              <Button
                                component={Link}
                                to={`/forum`}
                                size="small"
                                variant="outlined"
                                color="primary"
                                endIcon={<ArrowForward />}
                                sx={{
                                  borderRadius: 2,
                                  textTransform: 'none',
                                  fontWeight: 'medium',
                                  '&:hover': {
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                    transform: 'translateX(4px)',
                                  },
                                  transition: 'all 0.3s ease',
                                }}
                              >
                                Read More
                              </Button>
                            </Tooltip>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grow>
                  </Grid>
                ))}
              </Grid>

              <Box textAlign="center">
                <Tooltip title="Explore all discussions" arrow>
                  <Button
                    variant="contained"
                    color="secondary"
                    size="large"
                    component={Link}
                    to="/forum"
                    sx={{
                      px: 6,
                      py: 2.5,
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      borderRadius: 3,
                      boxShadow: '0 8px 25px rgba(245, 158, 11, 0.4)',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'translateY(-3px)',
                        boxShadow: '0 12px 35px rgba(245, 158, 11, 0.6)',
                      },
                    }}
                    startIcon={<Business />}
                  >
                    View All Discussions
                  </Button>
                </Tooltip>
              </Box>
            </>
          ) : (
            <Fade in={true} timeout={1000}>
              <Box textAlign="center" py={8}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 6,
                    borderRadius: 3,
                    bgcolor: 'grey.50',
                    border: '2px dashed',
                    borderColor: 'grey.300',
                  }}
                >
                  <Business sx={{ fontSize: 64, color: 'grey.400', mb: 3 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom sx={{ fontWeight: 'bold' }}>
                    No Recent Discussions Yet
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: '400px', mx: 'auto' }}>
                    Be the first to start a conversation and share your insights with the community!
                  </Typography>
                  <Button
                    component={Link}
                    to="/forum"
                    variant="contained"
                    color="primary"
                    size="large"
                    startIcon={<Business />}
                    sx={{
                      borderRadius: 2,
                      px: 4,
                      py: 1.5,
                      fontWeight: 'bold',
                    }}
                  >
                    Start a Discussion
                  </Button>
                </Paper>
              </Box>
            </Fade>
          )}
        </Container>
      </Box>

      {/* Partners Section */}
      <Box sx={{ py: 10, bgcolor: 'grey.50', position: 'relative', overflow: 'hidden' }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={8}>
            <Fade in={true} timeout={1000}>
              <Typography
                variant="h2"
                component="h2"
                color="primary"
                sx={{
                  mb: 3,
                  fontWeight: 'bold',
                  position: 'relative',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    bottom: -10,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 80,
                    height: 4,
                    bgcolor: 'secondary.main',
                    borderRadius: 2,
                  },
                }}
              >
                In Association With
              </Typography>
            </Fade>
            <Fade in={true} timeout={1500}>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{
                  maxWidth: '600px',
                  mx: 'auto',
                  lineHeight: 1.6,
                }}
              >
                Proud partners supporting our mission to advance pharmaceutical research and education
              </Typography>
            </Fade>
          </Box>

          <Grid container spacing={4}>
            {partners.map((partner, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Grow in={true} timeout={1000 + index * 300}>
                  <Card
                    elevation={1}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      p: 5,
                      borderRadius: 3,
                      position: 'relative',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      cursor: 'pointer',
                      border: '1px solid',
                      borderColor: 'grey.200',
                      '&:hover': {
                        transform: 'translateY(-8px) scale(1.02)',
                        boxShadow: (theme: any) => `0 16px 40px ${theme.palette.primary.main}15`,
                        borderColor: 'primary.light',
                        '& .partner-logo': {
                          transform: 'scale(1.05)',
                          filter: 'grayscale(0%)',
                        },
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 120,
                        height: 120,
                        borderRadius: 2,
                        bgcolor: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        p: 2,
                        mb: 3,
                        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <Box
                        component="img"
                        src={partner.logo}
                        alt={partner.name}
                        className="partner-logo"
                        sx={{
                          height: '100%',
                          width: 'auto',
                          maxWidth: '100%',
                          objectFit: 'contain',
                          filter: 'grayscale(100%)',
                          transition: 'all 0.3s ease',
                        }}
                      />
                    </Box>

                    <Typography
                      variant="h6"
                      sx={{
                        textAlign: 'center',
                        fontWeight: 'bold',
                        color: 'primary.main',
                        mb: 2,
                      }}
                    >
                      {partner.name}
                    </Typography>

                    <Divider sx={{ width: '60%', mb: 2, borderColor: 'primary.light' }} />

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        textAlign: 'center',
                        lineHeight: 1.6,
                        fontSize: '0.9rem',
                      }}
                    >
                      Supporting excellence in pharmaceutical education and research
                    </Typography>
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Container>

        {/* Background decorative elements */}
        <Box
          sx={{
            position: 'absolute',
            top: '10%',
            left: '10%',
            width: 100,
            height: 100,
            borderRadius: '50%',
            bgcolor: 'secondary.main',
            opacity: 0.03,
            zIndex: 0,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: '15%',
            right: '8%',
            width: 80,
            height: 80,
            borderRadius: '50%',
            bgcolor: 'primary.main',
            opacity: 0.04,
            zIndex: 0,
          }}
        />
      </Box>
    </Box>
  );
};

export default Home;
