"""init all tables

Revision ID: c2fd1ed012f9
Revises: 
Create Date: 2018-07-20 20:15:17.704564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2fd1ed012f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dj_admin_action_bill',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('action', sa.String(length=120), nullable=True),
    sa.Column('actionTime', sa.Integer(), nullable=True),
    sa.Column('actionDetail', sa.String(length=1024), nullable=True),
    sa.Column('actionIp', sa.String(length=120), nullable=True),
    sa.Column('actionMethod', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_betbill',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('matchId', sa.String(length=45), nullable=True),
    sa.Column('guessId', sa.String(length=45), nullable=True),
    sa.Column('playType', sa.String(length=45), nullable=True),
    sa.Column('roundNum', sa.Integer(), nullable=True),
    sa.Column('supportType', sa.String(length=45), nullable=True),
    sa.Column('betCoinNum', sa.Integer(), nullable=True),
    sa.Column('betTime', sa.Integer(), nullable=True),
    sa.Column('coinBeforeBet', sa.BigInteger(), nullable=True),
    sa.Column('coinAfterBet', sa.BigInteger(), nullable=True),
    sa.Column('guessLevelBeforeBet', sa.Integer(), nullable=True),
    sa.Column('guessLevelAfterBet', sa.Integer(), nullable=True),
    sa.Column('guessExpBeforeBet', sa.Integer(), nullable=True),
    sa.Column('guessExpAfterBet', sa.Integer(), nullable=True),
    sa.Column('projectType', sa.String(length=12), nullable=True),
    sa.Column('betHisUId', sa.String(length=45), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_betresultbill',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('matchType', sa.String(length=46), nullable=True),
    sa.Column('matchId', sa.String(length=45), nullable=True),
    sa.Column('guessName', sa.String(length=45), nullable=True),
    sa.Column('guessId', sa.String(length=45), nullable=True),
    sa.Column('playType', sa.String(length=45), nullable=True),
    sa.Column('roundNum', sa.Integer(), nullable=True),
    sa.Column('supportType', sa.String(length=45), nullable=True),
    sa.Column('rate', sa.Float(), nullable=True),
    sa.Column('betCoinNum', sa.Integer(), nullable=True),
    sa.Column('coinBeforeWin', sa.Integer(), nullable=True),
    sa.Column('coinAfterWin', sa.Integer(), nullable=True),
    sa.Column('winCoin', sa.Integer(), nullable=True),
    sa.Column('projectType', sa.String(length=12), nullable=True),
    sa.Column('resultTime', sa.Integer(), nullable=True),
    sa.Column('betTime', sa.Integer(), nullable=True),
    sa.Column('betResult', sa.String(length=255), nullable=True),
    sa.Column('vipLevel', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_filepos',
    sa.Column('hostName', sa.String(length=45), nullable=False),
    sa.Column('fileName', sa.String(length=128), nullable=True),
    sa.Column('seekPos', sa.Integer(), nullable=True),
    sa.Column('lastLogTime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('hostName')
    )
    op.create_table('dj_loginbill',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('loginTime', sa.Integer(), nullable=True),
    sa.Column('loginDevice', sa.String(length=45), nullable=True),
    sa.Column('loginIp', sa.String(length=45), nullable=True),
    sa.Column('coin', sa.BigInteger(), nullable=True),
    sa.Column('vipLevel', sa.Integer(), nullable=True),
    sa.Column('vipExp', sa.Integer(), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_paybill',
    sa.Column('orderId', sa.String(length=128), nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('payTime', sa.Integer(), nullable=True),
    sa.Column('payIp', sa.String(length=32), nullable=True),
    sa.Column('payCoin', sa.Integer(), nullable=True),
    sa.Column('payChannel', sa.String(length=45), nullable=True),
    sa.Column('orderState', sa.Integer(), nullable=True),
    sa.Column('firstPayCoin', sa.Integer(), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('firstPayTime', sa.Integer(), nullable=True),
    sa.Column('thirdPayOrder', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('orderId')
    )
    op.create_table('dj_pingbobetbill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wagerId', sa.Integer(), nullable=True),
    sa.Column('sport', sa.String(length=45), nullable=True),
    sa.Column('league', sa.String(length=45), nullable=True),
    sa.Column('eventName', sa.String(length=45), nullable=True),
    sa.Column('homeTeam', sa.String(length=45), nullable=True),
    sa.Column('awayTeam', sa.String(length=45), nullable=True),
    sa.Column('selection', sa.String(length=45), nullable=True),
    sa.Column('oddsFormat', sa.Integer(), nullable=True),
    sa.Column('odds', sa.Float(), nullable=True),
    sa.Column('stake', sa.Float(), nullable=True),
    sa.Column('betType', sa.SmallInteger(), nullable=True),
    sa.Column('eventDateFm', sa.Integer(), nullable=True),
    sa.Column('result', sa.String(length=32), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=True),
    sa.Column('toWin', sa.String(length=32), nullable=True),
    sa.Column('toRisk', sa.String(length=32), nullable=True),
    sa.Column('winLoss', sa.Float(), nullable=True),
    sa.Column('currencyCode', sa.String(length=32), nullable=True),
    sa.Column('exRate', sa.Float(), nullable=True),
    sa.Column('userCode', sa.String(length=45), nullable=True),
    sa.Column('loginId', sa.String(length=45), nullable=True),
    sa.Column('product', sa.String(length=32), nullable=True),
    sa.Column('wagerDateFm', sa.Integer(), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('settleDateFm', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_regbill',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('regTime', sa.String(length=45), nullable=True),
    sa.Column('regIp', sa.String(length=45), nullable=True),
    sa.Column('channel', sa.Integer(), nullable=True),
    sa.Column('regDevice', sa.String(length=45), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_shababetbill',
    sa.Column('transId', sa.BigInteger(), nullable=False),
    sa.Column('sportType', sa.Integer(), nullable=True),
    sa.Column('leagueId', sa.Integer(), nullable=True),
    sa.Column('homeId', sa.Integer(), nullable=True),
    sa.Column('awayId', sa.Integer(), nullable=True),
    sa.Column('betTeam', sa.String(length=45), nullable=True),
    sa.Column('oddsType', sa.SmallInteger(), nullable=True),
    sa.Column('odds', sa.Float(), nullable=True),
    sa.Column('stake', sa.Float(), nullable=True),
    sa.Column('betType', sa.SmallInteger(), nullable=True),
    sa.Column('ticketStatus', sa.String(length=10), nullable=True),
    sa.Column('winLostAmount', sa.Float(), nullable=True),
    sa.Column('currency', sa.SmallInteger(), nullable=True),
    sa.Column('vendorMemberId', sa.String(length=50), nullable=True),
    sa.Column('transActionTime', sa.Integer(), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('winLostDateTime', sa.Integer(), nullable=True),
    sa.Column('operatorId', sa.String(length=50), nullable=True),
    sa.Column('baStatus', sa.String(length=5), nullable=True),
    sa.Column('betTag', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('transId')
    )
    op.create_table('dj_withdrawalbill',
    sa.Column('orderId', sa.String(length=128), nullable=False),
    sa.Column('accountId', sa.String(length=32), nullable=True),
    sa.Column('withdrawalTime', sa.Integer(), nullable=True),
    sa.Column('withdrawalIp', sa.String(length=32), nullable=True),
    sa.Column('withdrawalCoin', sa.Integer(), nullable=True),
    sa.Column('cardNum', sa.String(length=20), nullable=True),
    sa.Column('orderState', sa.Integer(), nullable=True),
    sa.Column('agentId', sa.String(length=32), nullable=True),
    sa.Column('userType', sa.SmallInteger(), nullable=True),
    sa.PrimaryKeyConstraint('orderId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dj_withdrawalbill')
    op.drop_table('dj_shababetbill')
    op.drop_table('dj_regbill')
    op.drop_table('dj_pingbobetbill')
    op.drop_table('dj_paybill')
    op.drop_table('dj_loginbill')
    op.drop_table('dj_filepos')
    op.drop_table('dj_betresultbill')
    op.drop_table('dj_betbill')
    op.drop_table('dj_admin_action_bill')
    # ### end Alembic commands ###