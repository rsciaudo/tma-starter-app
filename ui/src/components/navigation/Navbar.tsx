import { Link, useNavigate } from 'react-router-dom';
import {
    Group,
    Button,
    Text,
    Container,
    Menu,
    Avatar,
    UnstyledButton,
    Stack,
    Box,
    Burger,
} from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
import { IconLogout, IconUser, IconChevronDown } from '@tabler/icons-react';
import { useAuth } from '../../contexts/AuthContext';
import { useSidebar } from '../../hooks/useSidebar';

interface NavLink {
    label: string;
    path: string;
}

export default function Navbar() {
    const { isAuthenticated, userInfo, logout } = useAuth();
    const navigate = useNavigate();
    const isMobile = useMediaQuery('(max-width: 768px)');
    const { drawerOpened, openDrawer, closeDrawer } = useSidebar();

    function handleLogout() {
        logout();
        navigate('/login');
    }

    // Don't show navbar if not authenticated
    if (!isAuthenticated) {
        return null;
    }

    // Determine available links based on user role
    const links: NavLink[] = [];

    // All authenticated users can see dashboard (content varies by role)
    links.push({ label: 'Dashboard', path: '/dashboard' });

    // User menu content (reusable for both desktop and mobile)
    const renderUserMenu = () => (
        <Menu
            shadow="md"
            width={200}
            position="bottom-end"
            withArrow
            offset={5}
            zIndex={1001}
        >
            <Menu.Target>
                <UnstyledButton className="min-w-0">
                    <Group
                        gap={isMobile ? 'xs' : 'sm'}
                        wrap="nowrap"
                        className="min-w-0"
                    >
                        <Avatar
                            color="primary"
                            radius="xl"
                            size="sm"
                            className="flex-shrink-0"
                        >
                            {userInfo?.username?.charAt(0).toUpperCase() || 'U'}
                        </Avatar>
                        {!isMobile && (
                            <Stack gap={0} className="min-w-0 flex-1">
                                <Group gap="xs" align="center" wrap="nowrap">
                                    <Text
                                        size="sm"
                                        fw={500}
                                        className="overflow-hidden text-ellipsis whitespace-nowrap"
                                    >
                                        {userInfo?.username || 'User'}
                                    </Text>
                                </Group>
                                <Text
                                    size="xs"
                                    className="overflow-hidden text-ellipsis whitespace-nowrap"
                                >
                                    {userInfo?.role?.name || 'user'}
                                </Text>
                            </Stack>
                        )}
                        {!isMobile && (
                            <IconChevronDown
                                size={16}
                                className="flex-shrink-0"
                            />
                        )}
                    </Group>
                </UnstyledButton>
            </Menu.Target>

            <Menu.Dropdown>
                <Menu.Label>Account</Menu.Label>
                <Menu.Item leftSection={<IconUser size={14} />}>
                    Profile
                </Menu.Item>
                <Menu.Item
                    leftSection={<IconLogout size={14} />}
                    color="red"
                    onClick={handleLogout}
                >
                    Logout
                </Menu.Item>
            </Menu.Dropdown>
        </Menu>
    );

    return (
        <Box
            className="fixed top-0 left-0 right-0 w-full z-[1000] border-b border-[var(--mantine-color-gray-2)] shadow-xs"
            style={{
                backgroundColor: 'var(--mantine-color-white)',
            }}
        >
            <Container
                size="xl"
                py={{ base: 'sm', sm: 'md' }}
                px={{ base: 'sm', sm: 'md' }}
            >
                <Group
                    justify="space-between"
                    align="center"
                    wrap="nowrap"
                    gap="md"
                >
                    {/* Mobile: Burger menu (replaces logo) | Desktop: Logo */}
                    {isMobile ? (
                        <Burger
                            opened={drawerOpened}
                            onClick={drawerOpened ? closeDrawer : openDrawer}
                            size="sm"
                            className="flex-shrink-0"
                        />
                    ) : (
                        <Text
                            fw={700}
                            size="lg"
                            component={Link}
                            to="/"
                            c="pink.6"
                            className="no-underline flex-shrink-0"
                        >
                            Logo
                        </Text>
                    )}

                    {/* User menu (always visible) */}
                    <Box className="flex-shrink-0 min-w-0">
                        {isMobile ? (
                            renderUserMenu()
                        ) : (
                            /* Desktop: Navigation Links and User Menu */
                            <Group gap="md" wrap="wrap">
                                {links.map((link) => (
                                    <Button
                                        key={link.path}
                                        component={Link}
                                        to={link.path}
                                        variant="subtle"
                                        size="sm"
                                    >
                                        {link.label}
                                    </Button>
                                ))}
                                {renderUserMenu()}
                            </Group>
                        )}
                    </Box>
                </Group>
            </Container>
        </Box>
    );
}
